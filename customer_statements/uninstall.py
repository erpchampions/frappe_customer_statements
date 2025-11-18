import frappe


def before_uninstall():
	"""Clean up any custom fields from old approach"""
	cleanup_old_custom_fields()


def cleanup_old_custom_fields():
	"""Remove custom fields that may have been created in previous version"""
	custom_fields = [
		"enable_multi_party_type",
		"party_type_section",
		"party_type",
		"party_collection",
		"party_collection_name",
		"column_break_party",
		"fetch_parties",
		"parties_section",
		"parties"
	]

	for fieldname in custom_fields:
		try:
			if frappe.db.exists("Custom Field", {"dt": "Process Statement of Accounts", "fieldname": fieldname}):
				frappe.delete_doc("Custom Field",
					frappe.db.get_value("Custom Field",
						{"dt": "Process Statement of Accounts", "fieldname": fieldname},
						"name"
					),
					force=True
				)
		except Exception as e:
			frappe.log_error(f"Error removing custom field {fieldname}: {str(e)}")

	frappe.db.commit()
	print("Cleanup: Removed old custom fields from Process Statement of Accounts")
