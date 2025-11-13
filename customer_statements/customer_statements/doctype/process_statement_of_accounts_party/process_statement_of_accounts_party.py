# Copyright (c) 2025, Cecypo.Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProcessStatementofAccountsParty(Document):
	def before_insert(self):
		"""Fetch party name and email before inserting"""
		self.fetch_party_details()

	def validate(self):
		"""Validate and fetch party details"""
		self.fetch_party_details()

	def fetch_party_details(self):
		"""Fetch party name and primary email from the party doctype"""
		if not self.party or not self.party_type:
			return

		# Get party details
		party_doc = frappe.get_cached_doc(self.party_type, self.party)

		# Fetch party name - different party types have different name fields
		self.party_name = self.get_party_name(party_doc)

		# Fetch primary email
		self.primary_email = self.get_party_email(party_doc)

	def get_party_name(self, party_doc):
		"""Get the display name for the party based on party type"""
		party_type = self.party_type

		name_field_map = {
			"Customer": "customer_name",
			"Supplier": "supplier_name",
			"Employee": "employee_name",
			"Shareholder": "shareholder_name",
			"Member": "member_name",
		}

		name_field = name_field_map.get(party_type)

		if name_field and hasattr(party_doc, name_field):
			return party_doc.get(name_field) or party_doc.name

		return party_doc.name

	def get_party_email(self, party_doc):
		"""Get primary email for the party"""
		# Try common email fields
		if hasattr(party_doc, "email_id") and party_doc.email_id:
			return party_doc.email_id

		if hasattr(party_doc, "email") and party_doc.email:
			return party_doc.email

		# For Customer/Supplier, try to get from Contact
		if self.party_type in ["Customer", "Supplier"]:
			return self.get_contact_email(party_doc.name)

		return None

	def get_contact_email(self, party_name):
		"""Get email from Contact doctype for Customer/Supplier"""
		contact = frappe.db.get_value(
			"Dynamic Link",
			{
				"link_doctype": self.party_type,
				"link_name": party_name,
				"parenttype": "Contact",
			},
			"parent",
		)

		if contact:
			email = frappe.db.get_value("Contact", contact, "email_id")
			return email

		return None
