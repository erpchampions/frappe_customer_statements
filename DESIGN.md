# Frappe Customer Statements - Multi-Party Type Design

## Overview
Extension of ERPNext's "Process Statement of Accounts" to support multiple party types (Supplier, Employee, Shareholder) while maintaining 100% backward compatibility with Customer-only mode.

## Design Principles

### 1. Fallback-First Architecture
- **Default Behavior**: When `enable_multi_party_type = 0`, app behaves identically to ERPNext core
- **Enhanced Mode**: When `enable_multi_party_type = 1`, unlock multi-party functionality
- **Zero Core Changes**: All customizations via hooks, overrides, and custom fields
- **Upgrade-Safe**: ERPNext version updates won't break functionality

### 2. Dynamic Party Type Support
- Party types pulled from Frappe's Party Type doctype
- No hardcoded party types - automatically supports future additions
- Currently supports: Customer, Supplier, Employee, Shareholder, Member

---

## Technical Implementation

### Phase 1: Custom Fields

#### Parent DocType: Process Statement of Accounts

**Master Control:**
```json
{
  "fieldname": "enable_multi_party_type",
  "fieldtype": "Check",
  "label": "Enable Multi-Party Type Statements",
  "default": 0,
  "description": "Enable support for Supplier, Employee, and other party types beyond Customer",
  "insert_after": "company"
}
```

**Party Type Selection:**
```json
{
  "fieldname": "party_type_section",
  "fieldtype": "Section Break",
  "label": "Party Type Configuration",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "enable_multi_party_type"
},
{
  "fieldname": "party_type",
  "fieldtype": "Link",
  "label": "Party Type",
  "options": "DocType",
  "get_query": "customer_statements.custom.process_statement_of_accounts.get_party_types",
  "default": "Customer",
  "mandatory_depends_on": "eval:doc.enable_multi_party_type",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "party_type_section"
},
{
  "fieldname": "party_collection",
  "fieldtype": "Select",
  "label": "Fetch Parties By",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "party_type"
},
{
  "fieldname": "collection_name",
  "fieldtype": "Dynamic Link",
  "label": "Collection Name",
  "options": "party_collection",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "party_collection"
},
{
  "fieldname": "column_break_party",
  "fieldtype": "Column Break",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "collection_name"
},
{
  "fieldname": "fetch_parties",
  "fieldtype": "Button",
  "label": "Fetch Parties",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "column_break_party"
}
```

**Parties Table:**
```json
{
  "fieldname": "parties_section",
  "fieldtype": "Section Break",
  "label": "Parties",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "fetch_parties"
},
{
  "fieldname": "parties",
  "fieldtype": "Table",
  "label": "Parties",
  "options": "Process Statement of Accounts Party",
  "mandatory_depends_on": "eval:doc.enable_multi_party_type",
  "depends_on": "eval:doc.enable_multi_party_type",
  "insert_after": "parties_section"
}
```

#### Child DocType: Process Statement of Accounts Party

**New DocType to Create:**
```json
{
  "name": "Process Statement of Accounts Party",
  "module": "Accounts",
  "istable": 1,
  "editable_grid": 1,
  "fields": [
    {
      "fieldname": "party_type",
      "fieldtype": "Link",
      "label": "Party Type",
      "options": "DocType",
      "in_list_view": 1,
      "reqd": 1,
      "fetch_from": "parent.party_type"
    },
    {
      "fieldname": "party",
      "fieldtype": "Dynamic Link",
      "label": "Party",
      "options": "party_type",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "party_name",
      "fieldtype": "Data",
      "label": "Party Name",
      "read_only": 1,
      "in_list_view": 1,
      "fetch_from": "party.name"
    },
    {
      "fieldname": "billing_email",
      "fieldtype": "Data",
      "label": "Billing Email",
      "in_list_view": 1
    },
    {
      "fieldname": "primary_email",
      "fieldtype": "Data",
      "label": "Primary Email",
      "read_only": 1
    }
  ]
}
```

---

### Phase 2: Client-Side Logic (JavaScript)

**File:** `customer_statements/public/js/process_statement_of_accounts.js`

**Key Features:**
1. **Field Visibility Toggle**: Show/hide based on `enable_multi_party_type` flag
2. **Dynamic Collection Options**: Update `party_collection` options based on `party_type`
3. **Fetch Parties Button**: Call custom server method
4. **Party Type Change Handler**: Clear parties table when party type changes

**Fields to Hide When Flag is ON:**
- `customer_collection`
- `collection_name` (original field)
- `customers` table
- `fetch_customers` button
- `territory` (AR-specific)
- `sales_partner` (AR-specific)
- `sales_person` (AR-specific)

**Dynamic Collection Options by Party Type:**
```javascript
const PARTY_COLLECTION_OPTIONS = {
    "Customer": ["Customer Group", "Territory", "Sales Partner", "Sales Person"],
    "Supplier": ["Supplier Group", "Supplier Type"],
    "Employee": ["Department", "Branch", "Employment Type"],
    "Shareholder": ["Shareholder Type"],
    "Member": ["Member Type"]
};
```

---

### Phase 3: Python Controller Override

**File:** `customer_statements/custom/process_statement_of_accounts.py`

**Key Methods:**

#### 1. Fetch Parties (Override `fetch_customers`)
```python
@frappe.whitelist()
def fetch_parties(self):
    """
    Fetch parties based on party_type and collection criteria.
    Fallback to core fetch_customers() if multi-party mode disabled.
    """
    if not self.enable_multi_party_type:
        # Use core ERPNext logic
        return super().fetch_customers()

    # Custom multi-party logic
    if self.party_type == "Customer":
        return self.fetch_customers_enhanced()
    elif self.party_type == "Supplier":
        return self.fetch_suppliers()
    elif self.party_type == "Employee":
        return self.fetch_employees()
    # ... extensible for other types
```

#### 2. Get Statement Dictionary (Override)
```python
def get_statement_dict(self, party, party_name=None):
    """
    Generate statement data for any party type.
    Fallback to core if multi-party disabled.
    """
    if not self.enable_multi_party_type:
        return super().get_statement_dict(party, party_name)

    # Determine party type and fetch appropriate data
    return self._get_party_statement(party, party_name)
```

#### 3. Backward Compatibility Sync
```python
def before_save(self):
    """Sync parties to customers table for core compatibility"""
    if self.enable_multi_party_type and self.party_type == "Customer":
        # Sync parties → customers for reports that still expect customers
        self.sync_parties_to_customers()

    super().before_save()

def sync_parties_to_customers(self):
    """Copy parties table data to customers table"""
    self.customers = []
    for party in self.parties:
        self.append("customers", {
            "customer": party.party,
            "customer_name": party.party_name,
            "billing_email": party.billing_email
        })
```

#### 4. Report Filter Generation
```python
def get_report_filters(self):
    """Generate filters for GL/AR reports based on party type"""
    if not self.enable_multi_party_type:
        return super().get_gl_filters() or super().get_ar_filters()

    filters = {
        "party_type": self.party_type,
        "party": [party.party for party in self.parties],
        "party_name": [party.party_name for party in self.parties],
        # ... other filters
    }
    return filters
```

---

### Phase 4: Template Updates

**Files to Update:**
- `customer_statements/templates/process_statement_of_accounts.html`
- `customer_statements/templates/process_statement_of_accounts_accounts_receivable.html`

#### Dynamic Party Type Labels
```jinja
{# Before (hardcoded) #}
{{ _("Customer: ") }} <b>{{ filters.party[0] }}</b>

{# After (dynamic) #}
{% if filters.party_type %}
{{ _(filters.party_type + ": ") }} <b>{{ filters.party[0] }}</b>
{% else %}
{{ _("Customer: ") }} <b>{{ filters.party[0] }}</b>
{% endif %}
```

#### Conditional Customer-Specific Fields
```jinja
{# Customer LPO field - only for Customers #}
{% if filters.party_type == "Customer" or not filters.party_type %}
<th style="width: 8%;">{{ _("Customer LPO No.") }}</th>
{% endif %}
```

#### Payment Entry Queries (Already Generic)
```jinja
{# This already works for all party types #}
{% set pdc = frappe.db.get_list('Payment Entry',
    filters={'reference_date': ['>', frappe.utils.nowdate()],
             'party': ['=', filters.party[0]]},
    fields=['posting_date', 'mode_of_payment', 'reference_date', 'paid_amount']) %}
```

---

### Phase 5: Hooks Registration

**File:** `customer_statements/hooks.py`

```python
# Doctype class override
override_doctype_class = {
    "Process Statement of Accounts": "customer_statements.custom.process_statement_of_accounts.CustomProcessStatementOfAccounts"
}

# Whitelisted method override
override_whitelisted_methods = {
    "erpnext.accounts.doctype.process_statement_of_accounts.process_statement_of_accounts.fetch_customers":
        "customer_statements.custom.process_statement_of_accounts.fetch_parties",
    "erpnext.accounts.doctype.process_statement_of_accounts.process_statement_of_accounts.download_statements":
        "customer_statements.custom.process_statement_of_accounts.download_statements"
}

# Client scripts
doctype_js = {
    "Process Statement of Accounts": "public/js/process_statement_of_accounts.js"
}

# Template overrides (already exists)
process_soa_html = {
    "General Ledger": ["customer_statements/templates/process_statement_of_accounts.html"],
    "Accounts Receivable": ["customer_statements/templates/process_statement_of_accounts_accounts_receivable.html"],
}

# Fixtures for custom fields and doctypes
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "=", "Process Statement of Accounts"],
            ["fieldname", "in", [
                "enable_multi_party_type",
                "party_type_section",
                "party_type",
                "party_collection",
                "collection_name",
                "column_break_party",
                "fetch_parties",
                "parties_section",
                "parties"
            ]]
        ]
    },
    {
        "dt": "DocType",
        "filters": [["name", "=", "Process Statement of Accounts Party"]]
    }
]
```

---

## Migration Strategy

### For Existing Users:
1. **No Action Required**: Default flag is OFF - everything works as before
2. **Opt-In**: Check "Enable Multi-Party Type Statements" to unlock features
3. **Data Safety**: Original `customers` table remains intact

### For New Features:
1. **Supplier Statements**: Check flag → Select "Supplier" → Fetch suppliers → Download
2. **Employee Statements**: Check flag → Select "Employee" → Fetch employees → Download
3. **Mixed Use**: Can toggle flag ON/OFF per document as needed

---

## Testing Strategy

### Test Case 1: Default Behavior (Flag OFF)
- [ ] Create new Process Statement of Accounts
- [ ] Verify `enable_multi_party_type` = 0
- [ ] Verify standard customer fields visible
- [ ] Verify new party fields hidden
- [ ] Download customer statement → Should work identical to core

### Test Case 2: Customer Mode (Flag ON)
- [ ] Check `enable_multi_party_type`
- [ ] Select Party Type = "Customer"
- [ ] Verify party fields visible, customer-specific fields hidden
- [ ] Fetch parties by Customer Group
- [ ] Download statements → Should match core output exactly

### Test Case 3: Supplier Mode (Flag ON)
- [ ] Check `enable_multi_party_type`
- [ ] Select Party Type = "Supplier"
- [ ] Fetch parties by Supplier Group
- [ ] Verify GL report shows supplier transactions
- [ ] Verify aging summary displays correctly
- [ ] Download PDF → Verify "Supplier:" label instead of "Customer:"

### Test Case 4: Employee Mode (Flag ON)
- [ ] Check `enable_multi_party_type`
- [ ] Select Party Type = "Employee"
- [ ] Fetch parties by Department
- [ ] Verify GL report filters work
- [ ] Download statements

### Test Case 5: Backward Compatibility
- [ ] Enable multi-party mode with Customer
- [ ] Verify `customers` table auto-populates
- [ ] Verify core email functionality still works
- [ ] Verify auto-email scheduler compatibility

---

## Future Enhancements

### Phase 6 (Optional): Enhanced Filters
- Territory-based filtering for Suppliers
- Department-based filtering for Employees
- Custom filters per party type

### Phase 7 (Optional): Bulk Operations
- Multi-party type selection in single document
- Generate separate statements per party type
- Consolidated cross-party reports

### Phase 8 (Optional): Analytics
- Party-wise aging analysis across types
- Comparative reports (Customer vs Supplier aging)
- Dashboard integration

---

## File Structure Summary

```
customer_statements/
├── customer_statements/
│   ├── custom/                                    # NEW
│   │   ├── __init__.py
│   │   └── process_statement_of_accounts.py       # Controller override
│   ├── doctype/                                   # NEW
│   │   └── process_statement_of_accounts_party/
│   │       ├── __init__.py
│   │       ├── process_statement_of_accounts_party.json
│   │       └── process_statement_of_accounts_party.py
│   ├── fixtures/                                  # NEW
│   │   └── custom_fields.json                     # Custom field definitions
│   ├── public/
│   │   └── js/                                    # NEW
│   │       └── process_statement_of_accounts.js   # Client-side logic
│   ├── templates/                                 # UPDATE
│   │   ├── process_statement_of_accounts.html     # Update labels
│   │   └── process_statement_of_accounts_accounts_receivable.html
│   └── hooks.py                                   # UPDATE
├── DESIGN.md                                      # This file
└── README.md
```

---

## ERPNext Core Dependencies

### Doctypes Used:
- Process Statement of Accounts (parent)
- Process Statement of Accounts Customer (child - kept for compatibility)
- Party Type (for dynamic party type list)
- Customer, Supplier, Employee, Shareholder, Member (party doctypes)

### Reports Used:
- General Ledger
- Accounts Receivable
- (Reports already support party filters in core)

### Core Methods Preserved:
- Email sending logic
- PDF generation
- Scheduler integration
- Auto-email functionality

---

## Open Questions / Decisions Needed

1. **Party Name Field Fetching**: Each party type has different name fields
   - Customer: `customer_name`
   - Supplier: `supplier_name`
   - Employee: `employee_name`
   - **Solution**: Use meta.get_field() to detect name field dynamically

2. **Accounts Receivable for Non-Customers**:
   - Should we allow AR report for Suppliers/Employees?
   - **Decision**: Limit AR to Customer only, force GL for others

3. **Email Fields**:
   - Different party types store emails differently
   - **Solution**: Create helper method `get_party_email()` that handles each type

4. **Aging Calculation**:
   - Does aging work same way for all party types?
   - **Decision**: Yes - based on posting_date or due_date regardless of party type

5. **Custom Print Formats**:
   - Should we support party-specific print formats?
   - **Decision**: Phase 2 enhancement - use single format initially

---

## Priority: Supplier Support

**Immediate Requirement**: Enable Supplier statements

**Quick Win Path**:
1. Create flag + party_type field
2. Create parties child doctype
3. Override fetch logic for Suppliers only
4. Update templates for "Supplier:" label
5. Test with General Ledger report
6. Defer Employee/Shareholder to Phase 2

**Supplier-Specific Considerations**:
- Use `Supplier Group` and `Supplier Type` for collections
- Aging typically based on `posting_date` (bills)
- Email from Contact doctype (same as Customer)
- Payment Entry already supports supplier party type ✓

---

## Success Criteria

- [ ] Flag OFF: 100% identical behavior to ERPNext core
- [ ] Flag ON + Customer: Same output as core, using new structure
- [ ] Flag ON + Supplier: Generates accurate supplier statements
- [ ] Templates show correct party type labels dynamically
- [ ] Payment entries display for all party types
- [ ] Aging calculations work for all party types
- [ ] Email functionality preserved
- [ ] Auto-email scheduler compatible
- [ ] Upgrade-safe (no core modifications)
- [ ] Well-documented for future maintenance
