# Copyright (c) 2025, Cecypo.Tech and contributors
# For license information, please see license.txt

import frappe


def after_install():
	"""Create custom fields after app installation"""
	create_custom_fields()


def create_custom_fields():
	"""Create custom fields for multi-party type support"""
	# Check if fields already exist
	if frappe.db.exists("Custom Field", {"dt": "Process Statement of Accounts", "fieldname": "enable_multi_party_type"}):
		return  # Fields already created

	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as make_custom_fields

	custom_fields = {
		"Process Statement of Accounts": [
			dict(
				fieldname="enable_multi_party_type",
				label="Enable Multi-Party Type Statements",
				fieldtype="Check",
				insert_after="company",
				default="0",
				description="Enable support for Supplier, Employee, and other party types beyond Customer",
			),
			dict(
				fieldname="party_type_section",
				label="Party Type Configuration",
				fieldtype="Section Break",
				insert_after="enable_multi_party_type",
				depends_on="eval:doc.enable_multi_party_type",
				collapsible=0,
			),
			dict(
				fieldname="party_type",
				label="Party Type",
				fieldtype="Link",
				options="DocType",
				insert_after="party_type_section",
				default="Customer",
				mandatory_depends_on="eval:doc.enable_multi_party_type",
				depends_on="eval:doc.enable_multi_party_type",
				description="Select the type of party for statements (Customer, Supplier, Employee, etc.)",
			),
			dict(
				fieldname="party_collection",
				label="Fetch Parties By",
				fieldtype="Select",
				insert_after="party_type",
				depends_on="eval:doc.enable_multi_party_type",
				description="Select how to filter and fetch parties",
			),
			dict(
				fieldname="party_collection_name",
				label="Collection Name",
				fieldtype="Dynamic Link",
				options="party_collection",
				insert_after="party_collection",
				depends_on="eval:doc.enable_multi_party_type && doc.party_collection",
			),
			dict(
				fieldname="column_break_party",
				fieldtype="Column Break",
				insert_after="party_collection_name",
				depends_on="eval:doc.enable_multi_party_type",
			),
			dict(
				fieldname="fetch_parties",
				label="Fetch Parties",
				fieldtype="Button",
				insert_after="column_break_party",
				depends_on="eval:doc.enable_multi_party_type",
			),
			dict(
				fieldname="parties_section",
				label="Parties",
				fieldtype="Section Break",
				insert_after="fetch_parties",
				depends_on="eval:doc.enable_multi_party_type",
				collapsible=0,
			),
			dict(
				fieldname="parties",
				label="Parties",
				fieldtype="Table",
				options="Process Statement of Accounts Party",
				insert_after="parties_section",
				mandatory_depends_on="eval:doc.enable_multi_party_type",
				depends_on="eval:doc.enable_multi_party_type",
			),
		]
	}

	make_custom_fields(custom_fields, update=True)
	frappe.db.commit()
