# Installation & Setup Guide

## Multi-Party Type Statement of Accounts

This guide will help you install and configure the enhanced Customer Statements app with multi-party type support.

---

## Prerequisites

- ERPNext v15 installed and running
- Bench access for app installation
- Administrator access to ERPNext

---

## Installation Steps

### Step 1: Install the App

Navigate to your bench directory and install the app:

```bash
cd ~/frappe-bench

# Install from your forked repository
bench get-app https://github.com/erpchampions/frappe_customer_statements.git

# Install the app to your site
bench --site [your-site-name] install-app customer_statements
```

### Step 2: Migrate Database

After installation, run migrations to create custom fields and the new child doctype:

```bash
bench --site [your-site-name] migrate
```

### Step 3: Clear Cache

Clear cache to ensure all changes are loaded:

```bash
bench --site [your-site-name] clear-cache
bench --site [your-site-name] clear-website-cache
```

### Step 4: Restart Bench

Restart your bench to load the Python controller overrides:

```bash
bench restart
```

---

## Post-Installation Configuration

### Option 1: Import Custom Fields via Fixtures

If custom fields don't auto-create during migration, you can import them manually:

```bash
# Export custom fields (for reference)
bench --site [your-site-name] export-fixtures

# Or manually create via UI - see "Manual Setup" below
```

### Option 2: Manual Setup

If fixtures don't work, you can manually create the custom fields:

1. **Login to ERPNext** as Administrator
2. **Go to:** Customize Form
3. **Select DocType:** Process Statement of Accounts
4. **Add the following fields:**

#### Field 1: Enable Multi-Party Type
- **Label:** Enable Multi-Party Type Statements
- **Type:** Check
- **Insert After:** company
- **Default:** 0
- **Description:** Enable support for Supplier, Employee, and other party types beyond Customer

#### Field 2: Party Type Section
- **Label:** Party Type Configuration
- **Type:** Section Break
- **Insert After:** enable_multi_party_type
- **Depends On:** eval:doc.enable_multi_party_type

#### Field 3: Party Type
- **Label:** Party Type
- **Type:** Link
- **Options:** DocType
- **Insert After:** party_type_section
- **Default:** Customer
- **Mandatory Depends On:** eval:doc.enable_multi_party_type
- **Depends On:** eval:doc.enable_multi_party_type

#### Field 4: Party Collection
- **Label:** Fetch Parties By
- **Type:** Select
- **Insert After:** party_type
- **Depends On:** eval:doc.enable_multi_party_type

#### Field 5: Collection Name
- **Label:** Collection Name
- **Type:** Dynamic Link
- **Options:** party_collection
- **Insert After:** party_collection
- **Depends On:** eval:doc.enable_multi_party_type && doc.party_collection

#### Field 6: Column Break
- **Type:** Column Break
- **Insert After:** collection_name
- **Depends On:** eval:doc.enable_multi_party_type

#### Field 7: Fetch Parties Button
- **Label:** Fetch Parties
- **Type:** Button
- **Insert After:** column_break_party
- **Depends On:** eval:doc.enable_multi_party_type

#### Field 8: Parties Section
- **Label:** Parties
- **Type:** Section Break
- **Insert After:** fetch_parties
- **Depends On:** eval:doc.enable_multi_party_type

#### Field 9: Parties Table
- **Label:** Parties
- **Type:** Table
- **Options:** Process Statement of Accounts Party
- **Insert After:** parties_section
- **Mandatory Depends On:** eval:doc.enable_multi_party_type
- **Depends On:** eval:doc.enable_multi_party_type

---

## Verification

### Verify Installation

1. **Check DocType exists:**
   - Go to: DocType List
   - Search for: "Process Statement of Accounts Party"
   - Should show the new child doctype

2. **Check Custom Fields:**
   - Go to: Process Statement of Accounts
   - Create new document
   - Verify "Enable Multi-Party Type Statements" checkbox appears below Company field

3. **Check JS Loading:**
   - Open browser console (F12)
   - Go to Process Statement of Accounts
   - Check for any JS errors
   - Enable the multi-party checkbox - fields should show/hide

4. **Check Python Override:**
   - Enable multi-party mode
   - Try to fetch parties
   - Should not give errors

---

## Usage

### Default Mode (Backward Compatible)

**For Customer Statements Only:**

1. Create new "Process Statement of Accounts"
2. Leave "Enable Multi-Party Type Statements" **unchecked**
3. Use standard Customer fields as before
4. Everything works exactly like ERPNext core

### Enhanced Mode (Multi-Party)

**For Supplier, Employee, or Other Party Types:**

1. Create new "Process Statement of Accounts"
2. **Check** "Enable Multi-Party Type Statements"
3. Notice:
   - Customer-specific fields are hidden
   - New party type fields appear
4. **Select Party Type:** (e.g., Supplier)
5. **Select Fetch Parties By:** (e.g., Supplier Group)
6. **Select Collection Name:** (e.g., "Raw Material Suppliers")
7. **Click "Fetch Parties"** button
8. Review the populated parties table
9. Configure other settings (from/to dates, report type, etc.)
10. **Click "Download"** to generate statements

---

## Party Type Options

### Customer
**Fetch By Options:**
- Customer Group
- Territory
- Sales Partner
- Sales Person

### Supplier
**Fetch By Options:**
- Supplier Group
- Supplier Type

### Employee
**Fetch By Options:**
- Department
- Branch
- Employment Type

### Shareholder
**Fetch By Options:**
- Shareholder Type

### Member
**Fetch By Options:**
- Member Type

---

## Supported Reports

### General Ledger (Recommended for all party types)
- Works with all party types
- Shows complete transaction history
- Includes aging summary
- Future payments section

### Accounts Receivable (Customer-focused)
- Recommended for Customers only
- Can work with other party types but may have limited data
- Shows aging buckets
- LPO field only visible for Customers

### Accounts Payable (Supplier-focused)
- System will auto-use this for Suppliers
- Shows supplier aging
- Future payment obligations

---

## Troubleshooting

### Custom Fields Not Showing
**Solution:**
```bash
bench --site [your-site] clear-cache
bench --site [your-site] migrate
bench restart
```

### Fetch Parties Button Not Working
**Possible Causes:**
1. Party Type not selected
2. Collection Type/Name not selected
3. JS not loaded properly

**Solution:**
- Check browser console for errors
- Ensure bench restart was done
- Try hard refresh (Ctrl+Shift+R)

### Templates Not Updating
**Solution:**
```bash
bench --site [your-site] clear-website-cache
bench build --app customer_statements
bench restart
```

### Python Errors When Downloading
**Check:**
- Ensure override_doctype_class is in hooks.py
- Verify CustomProcessStatementOfAccounts class exists
- Check Python error logs: `bench --site [your-site] console`

**Error Log Location:**
```
~/frappe-bench/sites/[your-site]/logs/
```

### Party Type Field Not Filtering
**Note:** The party_type field currently shows all doctypes. For production, you may want to add a custom query filter to show only party-enabled doctypes.

---

## Testing Checklist

### Test 1: Default Mode (Customer Only)
- [ ] Create new Process Statement of Accounts
- [ ] Leave multi-party flag OFF
- [ ] Verify standard customer fields visible
- [ ] Fetch customers using standard method
- [ ] Download customer statement
- [ ] Verify output matches core ERPNext

### Test 2: Customer Mode (Enhanced)
- [ ] Create new Process Statement of Accounts
- [ ] Enable multi-party flag
- [ ] Select Party Type = Customer
- [ ] Fetch by Customer Group
- [ ] Download statements
- [ ] Verify output identical to Test 1

### Test 3: Supplier Mode
- [ ] Create new Process Statement of Accounts
- [ ] Enable multi-party flag
- [ ] Select Party Type = Supplier
- [ ] Fetch by Supplier Group
- [ ] Select General Ledger report
- [ ] Download statements
- [ ] Verify:
  - Header shows "Supplier:" instead of "Customer:"
  - LPO field not visible
  - Transactions display correctly
  - Aging summary shows

### Test 4: Employee Mode
- [ ] Create new Process Statement of Accounts
- [ ] Enable multi-party flag
- [ ] Select Party Type = Employee
- [ ] Fetch by Department
- [ ] Download General Ledger statements
- [ ] Verify employee transactions display

### Test 5: Email Functionality
- [ ] Enable auto-email
- [ ] Configure email settings
- [ ] Test with Customer party type
- [ ] Test with Supplier party type
- [ ] Verify emails sent correctly

---

## Known Limitations

1. **Party Type Selection:** Currently shows all doctypes. May need custom filtering in production.

2. **Accounts Receivable Report:** Optimized for Customers. Other party types should use General Ledger.

3. **Email Templates:** Currently use standard template for all party types. Future enhancement: party-type-specific templates.

4. **Performance:** Fetching large numbers of parties may be slow. Consider adding pagination in future.

---

## Upgrade Notes

### From Customer-Only Version

If upgrading from an older customer-only version:

1. **Existing documents are safe:** The multi-party flag defaults to OFF
2. **No data migration needed:** Old customer tables remain intact
3. **Opt-in enhancement:** Enable flag only when ready to use multi-party
4. **Backward compatible:** Can mix old and new documents in same site

### Future ERPNext Upgrades

- This app uses official Frappe/ERPNext override mechanisms
- Should be upgrade-safe for ERPNext v15 → v16
- Always test in development environment first
- Rebuild app after ERPNext upgrade: `bench build --app customer_statements`

---

## Support & Contribution

### Reporting Issues

Please report issues at: https://github.com/erpchampions/frappe_customer_statements/issues

Include:
- ERPNext version
- Python error logs
- Steps to reproduce
- Screenshots

### Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Submit pull request with detailed description

---

## License

AGPL-3.0 (same as ERPNext)

---

## Credits

- **Original App:** Cecypo.Tech
- **Multi-Party Enhancement:** 2025
- **Built on:** Frappe Framework & ERPNext
