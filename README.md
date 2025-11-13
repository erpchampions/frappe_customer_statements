# Customer Statements

Our first open source app for Frappe's ERPNext!

# Better **Statements**
- Prettier & more compact for both; **GENERAL LEDGER** & **ACCOUNTS RECEIVABLE**
- `Show Remarks` shows/hides the whole column for better spacing
- Better formatting for `terms & conditions`
- Includes `Future Payments` in a compact list
- **Configurable Signature Section** for printed reports (off by default)
- Includes custom fields for Kenyan based TIMS (e-invoicing) integrations, but should not effect you, should you not use such

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
$ bench get-app https://github.com/Cecypo-Tech/frappe_customer_statements.git
$ bench --site <site_name> install-app customer_statements
```

## Configuration

### Signature Section

The app includes an optional signature section for printed reports. This feature is **disabled by default** to maintain standard behavior.

**To enable and configure:**

1. Go to **Customer Statements Settings** (search in Awesome Bar)
2. Check **Enable Signature Section**
3. Customize the labels (default: "Prepared By", "Reviewed By", "Approved By")
4. Toggle **Show Name Field** and **Show Date Field** as needed
5. Save the settings

The signature section will appear at the bottom of printed statements with:
- Three signature lines (Prepared By, Reviewed By, Approved By)
- Optional name and date fields below each signature
- Space for physical signatures (50px height)
- Page-break protection to keep signatures on same page

**Affected Reports:**
- General Ledger Statement
- Accounts Receivable Statement

#### Other
If you are interested in our TIMS Integration (Kenya), see our (paid) direct integration tool here: https://docs.cecypo.tech/s/kb/doc/erpnext-O7U5xeE9DN

#### License

agpl-3.0