# Multi Party Statement - Implementation Summary

## Overview
Standalone doctype for generating statements for any party type (Customer, Supplier, Employee, etc.), following ERPNext v15 core patterns exactly.

## Key Design Decisions

### 1. Standalone Doctype (Not Custom Fields)
- **Why**: Avoids core modification, simpler installation, no migration conflicts
- **Benefit**: Clean uninstall, no schema changes to core doctypes

### 2. Field Order Matches Core
Following Process Statement of Accounts pattern:
1. Report selection FIRST
2. All filters grouped together (dates, company, account, etc.)
3. Party collection section
4. Parties table
5. Preferences & display options
6. Email settings

### 3. Template Reuse via Hooks
- Uses `process_soa_html` hook to reuse existing templates
- Templates from forked repo (erpchampions/frappe_customer_statements)
- No template duplication - hooks provide the templates

### 4. Data Processing Matches Core Exactly
- GL: Skip if len(res) == 3 (only header/footer, no transactions)
- AR: Skip if not res (no data)
- Quote cleanup: Remove ' from account names in rows [0, -2, -1]
- Critical filters: show_opening_entries: 0, include_default_book_entries: 0

### 5. Validation Strategy
- Field-level validation minimal (only dates)
- Parties required only on submit (not save)
- Allows workflow: Create → Save → Fetch → Submit

## Critical Filters (Prevents Duplicates)

### General Ledger
```python
{
    "show_opening_entries": 0,           # CRITICAL: No duplicate opening
    "include_default_book_entries": 0,   # CRITICAL: No duplicate books
    "show_cancelled_entries": 0,
    "categorize_by": "...",
    "currency": presentation_currency,
    "tax_id": "...",
    # ... other filters
}
```

### Accounts Receivable
```python
{
    "report_date": posting_date,
    "ageing_based_on": "...",
    "range1": 30, "range2": 60, "range3": 90, "range4": 120,
    "tax_id": "...",
    # ... other filters
}
```

## Template Context (Matches Core)
```python
{
    "filters": filters,              # Full filter dict
    "data": res,                     # Report results (cleaned)
    "report": {
        "report_name": "...",
        "columns": columns
    },
    "ageing": ageing,                # Ageing data if enabled
    "letter_head": {                 # Letterhead content/footer
        "content": "...",
        "footer": "..."
    },
    "terms_and_conditions": "",      # Future extension
    "age_as_on": posting_date
}
```

## PDF Generation (Matches Core)
1. Generate HTML for each party
2. Join with page breaks: `<div style="page-break-before: always;"></div>`
3. Convert combined HTML to PDF
4. Return base64 encoded for download

## Known Patterns From Core

### Empty Data Handling
- GL: `if len(res) == 3: continue` (exactly 3 = no real data)
- AR: `if not res: continue` (completely empty)

### Data Cleanup
- Remove quotes from account names: `res[x]["account"].replace("'", "")`
- Process rows: [0, -2, -1] (first, second-to-last, last)

### Template Wrapping
1. Render report template with context
2. Wrap in printview.html with:
   - `body`: rendered HTML
   - `css`: get_print_style()
   - `title`: "Statement For {party_name}"

## Comparison with Core

| Aspect | Core (Process Statement of Accounts) | This (Multi Party Statement) |
|--------|--------------------------------------|------------------------------|
| Party Types | Customer only | Any party type |
| Fields | Custom fields | Built-in fields |
| Installation | No migration needed | No migration needed |
| Templates | ERPNext core | Via hooks (same templates) |
| Filters | Core filters | Same filters |
| Data processing | Core pattern | Exact same pattern |
| PDF generation | Core approach | Exact same approach |
| Validation | On save | On submit only |

## Files Structure

```
customer_statements/
├── customer_statements/
│   └── doctype/
│       ├── multi_party_statement/
│       │   ├── multi_party_statement.json  # Doctype def
│       │   ├── multi_party_statement.py    # Business logic
│       │   └── multi_party_statement.js    # Client script
│       └── process_statement_of_accounts_party/
│           ├── *.json                       # Child doctype
│           └── *.py                         # Party details
├── templates/
│   ├── process_statement_of_accounts.html  # GL template
│   └── process_statement_of_accounts_accounts_receivable.html  # AR template
├── hooks.py                                 # Template hooks
└── uninstall.py                            # Cleanup script
```

## ERPNext Version
- Target: v15.88+
- Tested on: ERPNext v15
- Compatible: Should work on v14+ (uses stable APIs)

## References
- Core implementation: https://github.com/frappe/erpnext/blob/develop/erpnext/accounts/doctype/process_statement_of_accounts/
- Forked templates: https://github.com/erpchampions/frappe_customer_statements
