import frappe


def before_uninstall():
	"""Remove custom fields created by this app"""
	remove_custom_fields()


def remove_custom_fields():
	"""Delete custom fields added to Process Statement of Accounts"""
	custom_fields = [
		"enable_multi_party_type",
		"party_type",
		"party_collection",
		"party_collection_name",
		"column_break_party",
		"fetch_parties",
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
				frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error removing custom field {fieldname}: {str(e)}")

	print("Custom fields removed successfully")
