# Migration Guide

## Upgrading from Old Version (Custom Fields Approach)

If you previously installed the custom fields version of this app, you need to clean up the old custom fields before using the new Multi Party Statement doctype.

### Steps:

1. **Pull the latest changes**
   ```bash
   cd /workspace/development/frappe-bench/apps/customer_statements
   git pull origin claude/customize-frappe-customer-statements-011CV5XYuLWepVAfQvkECkuw
   ```

2. **Run cleanup script in Frappe console**
   ```bash
   bench --site your-site-name console
   ```

   Then in the console:
   ```python
   from customer_statements.uninstall import cleanup_old_custom_fields
   cleanup_old_custom_fields()
   ```

3. **Migrate the site**
   ```bash
   bench --site your-site-name migrate
   bench --site your-site-name clear-cache
   ```

4. **Verify cleanup**
   Check that custom fields are removed from Process Statement of Accounts doctype:
   ```bash
   bench --site your-site-name console
   ```

   ```python
   import frappe
   frappe.get_meta("Process Statement of Accounts").get_custom_fields()
   # Should return empty list or not include the fields we added
   ```

### New Doctype: Multi Party Statement

The new approach uses a completely standalone doctype called **Multi Party Statement** which:

- Does NOT modify the core ERPNext Process Statement of Accounts doctype
- Has all fields built-in (no custom fields)
- Supports Customer, Supplier, Employee, and other party types
- Can be used alongside the standard Process Statement of Accounts

### Key Differences:

| Old Approach | New Approach |
|-------------|--------------|
| Customizes core doctype | Standalone doctype |
| Adds custom fields | All fields built-in |
| Overrides controllers | Independent implementation |
| Complex migration | Simple installation |
| Risk of conflicts | No conflicts |

### Usage:

1. Go to **Accounting > Multi Party Statement > New**
2. Select Company, Report Type, Date Range
3. Select Party Type (Customer, Supplier, Employee, etc.)
4. Optionally select collection criteria (e.g., Customer Group, Supplier Group)
5. Click "Fetch Parties" button
6. Review the parties list, add/remove as needed
7. Save and Submit to generate statements

### Benefits of New Approach:

✓ No database schema conflicts
✓ No custom field collision
✓ Easier to maintain
✓ Cleaner uninstall
✓ Can coexist with core functionality
✓ Supports all party types from day one
