# Customer Statements

Our first open source app for Frappe's ERPNext!

# Better **Statements**
- Prettier & more compact for both; **GENERAL LEDGER** & **ACCOUNTS RECEIVABLE**
- `Show Remarks` shows/hides the whole column for better spacing
- Better formatting for `terms & conditions`
- Includes `Future Payments` in a compact list
- Includes custom fields for Kenyan based TIMS (e-invoicing) integrations, but should not effect you, should you not use such

# Multi-Party Type Support (NEW!)
- **Flexible Party Selection**: Generate statements for Customers, Suppliers, Employees, Shareholders, and more
- **Opt-In Enhancement**: Enable multi-party mode only when needed - 100% backward compatible
- **Dynamic Fetching**: Fetch parties by relevant criteria (Customer Group, Supplier Group, Department, etc.)
- **Smart Templates**: Automatically adapts labels and fields based on party type
- **Zero Core Modification**: Uses official ERPNext override mechanisms - upgrade-safe

## Features
- **Default Mode**: Works exactly like ERPNext core (Customer-only)
- **Enhanced Mode**: Unlock multi-party functionality with a single checkbox
- **Party Types Supported**: Customer, Supplier, Employee, Shareholder, Member (extensible)
- **Reports**: General Ledger (all types), Accounts Receivable (Customer-focused), Accounts Payable (Supplier-focused)

See [DESIGN.md](DESIGN.md) for architecture details and [INSTALLATION.md](INSTALLATION.md) for setup instructions.

# Screenshots
## What does this app effect?
![Effect](https://i.imgur.com/b1YIDEy.png)
## General Ledger
![Statement of Account](https://i.imgur.com/2vEajDZ.png)
## Accounts Receivable
![Accounts Receivable](https://i.imgur.com/uR4KSbZ.png)
## Sample with letterhead set (for multi-company setups)
![Letterhead](https://i.imgur.com/ZB5rrWE.png)
## Installation

```bash
# Install from repository
$ bench get-app https://github.com/erpchampions/frappe_customer_statements.git
$ bench --site <site_name> install-app customer_statements

# Migrate to create custom fields
$ bench --site <site_name> migrate

# Clear cache and restart
$ bench --site <site_name> clear-cache
$ bench restart
```

For detailed installation and configuration instructions, see [INSTALLATION.md](INSTALLATION.md).

For comprehensive testing checklist, see [TESTING.md](TESTING.md).

#### Other
If you are interested in our TIMS Integration (Kenya), see our (paid) direct integration tool here: https://docs.cecypo.tech/s/kb/doc/erpnext-O7U5xeE9DN

#### License

agpl-3.0