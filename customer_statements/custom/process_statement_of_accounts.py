# Copyright (c) 2025, Cecypo.Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate
from erpnext.accounts.doctype.process_statement_of_accounts.process_statement_of_accounts import (
	ProcessStatementOfAccounts,
)


class CustomProcessStatementOfAccounts(ProcessStatementOfAccounts):
	"""
	Extended Process Statement of Accounts with multi-party type support.
	Maintains 100% backward compatibility when enable_multi_party_type is disabled.
	"""

	def before_save(self):
		"""Sync parties to customers table for backward compatibility"""
		super().before_save()

		# If multi-party mode enabled and party type is Customer, sync to customers table
		if self.enable_multi_party_type and self.party_type == "Customer" and self.parties:
			self.sync_parties_to_customers()

	def sync_parties_to_customers(self):
		"""Copy parties table data to customers table for core compatibility"""
		self.customers = []
		for party in self.parties:
			if party.party_type == "Customer":
				self.append(
					"customers",
					{
						"customer": party.party,
						"customer_name": party.party_name,
						"billing_email": party.billing_email or party.primary_email,
					},
				)

	def get_statement_dict(self, party=None, party_name=None, customer=None, customer_name=None):
		"""
		Override to support multi-party types.
		Falls back to core logic if multi-party mode is disabled.
		"""
		# Fallback to core if multi-party disabled
		if not self.enable_multi_party_type:
			return super().get_statement_dict(customer=customer, customer_name=customer_name)

		# Multi-party mode enabled
		party_type = self.party_type or "Customer"

		# Use party parameters if provided, otherwise fallback to customer
		if not party and customer:
			party = customer
			party_name = customer_name

		if not party:
			return {}

		statement_dict = {}
		statement_dict["party"] = party
		statement_dict["party_name"] = party_name or party
		statement_dict["party_type"] = party_type

		# Get report filters based on party type
		filters = self.get_party_filters(party, party_type)

		# Get report data
		report_data = self.get_report_data(filters)

		# Process report data
		if report_data:
			statement_dict["data"] = report_data

			# Get aging if enabled
			if self.enable_auto_email and self.filter_duration:
				statement_dict["ageing"] = self.get_ageing(party, party_type)
			elif self.include_ageing:
				statement_dict["ageing"] = self.get_ageing(party, party_type)

		return statement_dict

	def get_party_filters(self, party, party_type):
		"""Generate report filters based on party type"""
		filters = frappe._dict()

		# Common filters
		filters.company = self.company
		filters.from_date = self.from_date
		filters.to_date = self.to_date
		filters.party_type = party_type
		filters.party = [party]

		# Report-specific filters
		if self.report == "General Ledger":
			filters.update(self.get_gl_party_filters(party, party_type))
		elif self.report == "Accounts Receivable":
			filters.update(self.get_ar_party_filters(party, party_type))

		return filters

	def get_gl_party_filters(self, party, party_type):
		"""Get General Ledger specific filters for party"""
		filters = frappe._dict()

		# Party account
		if party_type == "Customer":
			filters.account = self.get_party_account(party, party_type) or self.account
			filters.party_type = "Customer"
			filters.customer = party
		elif party_type == "Supplier":
			filters.account = self.get_party_account(party, party_type) or self.account
			filters.party_type = "Supplier"
			filters.supplier = party
		else:
			filters.account = self.get_party_account(party, party_type) or self.account
			filters.party_type = party_type
			filters.party = party

		# Other GL filters
		if self.finance_book:
			filters.finance_book = self.finance_book
		if self.cost_center:
			filters.cost_center = [d.cost_center_name for d in self.cost_center]
		if self.project:
			filters.project = [d.project_name for d in self.project]

		filters.group_by = "Group by Voucher (Consolidated)" if self.consolidate_vouchers else "Group by Voucher"

		if hasattr(self, "show_net_values_in_party_account"):
			filters.show_net_values_in_party_account = self.show_net_values_in_party_account
		if hasattr(self, "ignore_exchange_rate_revaluation_journals"):
			filters.ignore_exchange_rate_revaluation_journals = self.ignore_exchange_rate_revaluation_journals
		if hasattr(self, "ignore_cr_dr_notes"):
			filters.ignore_cr_dr_notes = self.ignore_cr_dr_notes

		return filters

	def get_ar_party_filters(self, party, party_type):
		"""Get Accounts Receivable specific filters for party"""
		filters = frappe._dict()

		# AR is primarily for Customers, but can work for other receivables
		if party_type == "Customer":
			filters.customer = party
		elif party_type == "Supplier":
			# For supplier, we might want Accounts Payable instead
			filters.supplier = party
		else:
			filters.party_type = party_type
			filters.party = party

		# AR specific filters
		filters.report_date = self.report_date or self.to_date
		filters.ageing_based_on = self.ageing_based_on

		if hasattr(self, "based_on_payment_terms"):
			filters.based_on_payment_terms = self.based_on_payment_terms
		if hasattr(self, "payment_terms_template"):
			filters.payment_terms_template = self.payment_terms_template
		if hasattr(self, "show_future_payments"):
			filters.show_future_payments = self.show_future_payments
		if hasattr(self, "show_remarks"):
			filters.show_remarks = self.show_remarks

		return filters

	def get_party_account(self, party, party_type):
		"""Get the party account for the given party type"""
		try:
			from erpnext.accounts.party import get_party_account
			return get_party_account(party_type, party, self.company)
		except Exception:
			return None

	def get_report_data(self, filters):
		"""Execute report and get data"""
		report_name = self.report

		try:
			report = frappe.get_doc("Report", report_name)
			columns, data = report.get_data(
				filters=filters,
				as_dict=True,
				ignore_prepared_report=True,
				are_default_filters=False
			)
			return data
		except Exception as e:
			frappe.log_error(f"Error getting report data: {str(e)}")
			return []

	def get_ageing(self, party, party_type):
		"""Get ageing data for party"""
		ageing_filters = frappe._dict()
		ageing_filters.company = self.company
		ageing_filters.report_date = self.report_date or self.to_date
		ageing_filters.ageing_based_on = self.ageing_based_on
		ageing_filters.range1 = 30
		ageing_filters.range2 = 60
		ageing_filters.range3 = 90
		ageing_filters.range4 = 120

		if party_type == "Customer":
			ageing_filters.customer = party
		elif party_type == "Supplier":
			ageing_filters.supplier = party
		else:
			ageing_filters.party_type = party_type
			ageing_filters.party = party

		# Get ageing report
		try:
			if party_type == "Supplier":
				report_name = "Accounts Payable"
			else:
				report_name = "Accounts Receivable"

			report = frappe.get_doc("Report", report_name)
			columns, data = report.get_data(
				filters=ageing_filters,
				as_dict=True,
				ignore_prepared_report=True,
				are_default_filters=False
			)

			# Calculate ageing summary
			if data:
				ageing = frappe._dict()
				ageing.ageing_based_on = self.ageing_based_on
				ageing.range1 = sum(flt(d.get("range1", 0)) for d in data)
				ageing.range2 = sum(flt(d.get("range2", 0)) for d in data)
				ageing.range3 = sum(flt(d.get("range3", 0)) for d in data)
				ageing.range4 = sum(flt(d.get("range4", 0)) for d in data)
				ageing.range5 = sum(flt(d.get("range5", 0)) for d in data)
				return ageing
		except Exception as e:
			frappe.log_error(f"Error getting ageing data: {str(e)}")

		return None


# Whitelisted methods

@frappe.whitelist()
def fetch_parties(docname):
	"""
	Fetch parties based on party_type and collection criteria.
	Fallback to core fetch_customers() if multi-party mode disabled.
	"""
	doc = frappe.get_doc("Process Statement of Accounts", docname)

	# Fallback to core if multi-party disabled
	if not doc.enable_multi_party_type:
		return doc.fetch_customers()

	# Validate required fields
	if not doc.party_type:
		frappe.throw(_("Please select Party Type"))

	party_type = doc.party_type
	collection_type = doc.party_collection
	collection_name = doc.collection_name

	# Clear existing parties
	doc.parties = []

	# Fetch parties based on collection type
	parties = []

	if party_type == "Customer":
		parties = fetch_customers_by_collection(doc, collection_type, collection_name)
	elif party_type == "Supplier":
		parties = fetch_suppliers_by_collection(doc, collection_type, collection_name)
	elif party_type == "Employee":
		parties = fetch_employees_by_collection(doc, collection_type, collection_name)
	else:
		parties = fetch_generic_parties(doc, party_type, collection_type, collection_name)

	# Add parties to document
	for party_data in parties:
		doc.append("parties", party_data)

	doc.save()
	frappe.msgprint(_("Parties fetched successfully"))


def fetch_customers_by_collection(doc, collection_type, collection_name):
	"""Fetch customers based on collection type"""
	parties = []

	if not collection_type or not collection_name:
		return parties

	if collection_type in ["Customer Group", "Territory"]:
		# Use hierarchical fetching
		lft, rgt = frappe.db.get_value(collection_type, collection_name, ["lft", "rgt"])
		customers = frappe.get_all(
			"Customer",
			filters={
				collection_type.lower().replace(" ", "_"): (
					"in",
					frappe.db.sql_list(
						f"""select name from `tab{collection_type}`
						where lft >= {lft} and rgt <= {rgt}"""
					),
				),
				"disabled": 0,
			},
			fields=["name", "customer_name", "email_id"],
		)

		for customer in customers:
			parties.append(
				{
					"party_type": "Customer",
					"party": customer.name,
					"party_name": customer.customer_name,
					"primary_email": customer.email_id,
				}
			)

	elif collection_type == "Sales Partner":
		customers = frappe.get_all(
			"Customer",
			filters={"default_sales_partner": collection_name, "disabled": 0},
			fields=["name", "customer_name", "email_id"],
		)

		for customer in customers:
			parties.append(
				{
					"party_type": "Customer",
					"party": customer.name,
					"party_name": customer.customer_name,
					"primary_email": customer.email_id,
				}
			)

	elif collection_type == "Sales Person":
		# Get customers from sales team
		sales_team_entries = frappe.get_all(
			"Sales Team",
			filters={"sales_person": collection_name, "parenttype": "Customer"},
			fields=["parent"],
		)

		customer_names = [d.parent for d in sales_team_entries]

		if customer_names:
			customers = frappe.get_all(
				"Customer",
				filters={"name": ("in", customer_names), "disabled": 0},
				fields=["name", "customer_name", "email_id"],
			)

			for customer in customers:
				parties.append(
					{
						"party_type": "Customer",
						"party": customer.name,
						"party_name": customer.customer_name,
						"primary_email": customer.email_id,
					}
				)

	return parties


def fetch_suppliers_by_collection(doc, collection_type, collection_name):
	"""Fetch suppliers based on collection type"""
	parties = []

	if not collection_type or not collection_name:
		return parties

	if collection_type == "Supplier Group":
		# Use hierarchical fetching
		lft, rgt = frappe.db.get_value("Supplier Group", collection_name, ["lft", "rgt"])
		suppliers = frappe.get_all(
			"Supplier",
			filters={
				"supplier_group": (
					"in",
					frappe.db.sql_list(
						f"""select name from `tabSupplier Group`
						where lft >= {lft} and rgt <= {rgt}"""
					),
				),
				"disabled": 0,
			},
			fields=["name", "supplier_name", "email_id"],
		)

		for supplier in suppliers:
			parties.append(
				{
					"party_type": "Supplier",
					"party": supplier.name,
					"party_name": supplier.supplier_name,
					"primary_email": supplier.email_id,
				}
			)

	elif collection_type == "Supplier Type":
		suppliers = frappe.get_all(
			"Supplier",
			filters={"supplier_type": collection_name, "disabled": 0},
			fields=["name", "supplier_name", "email_id"],
		)

		for supplier in suppliers:
			parties.append(
				{
					"party_type": "Supplier",
					"party": supplier.name,
					"party_name": supplier.supplier_name,
					"primary_email": supplier.email_id,
				}
			)

	return parties


def fetch_employees_by_collection(doc, collection_type, collection_name):
	"""Fetch employees based on collection type"""
	parties = []

	if not collection_type or not collection_name:
		return parties

	filters = {"status": "Active"}

	if collection_type == "Department":
		filters["department"] = collection_name
	elif collection_type == "Branch":
		filters["branch"] = collection_name
	elif collection_type == "Employment Type":
		filters["employment_type"] = collection_name

	employees = frappe.get_all(
		"Employee",
		filters=filters,
		fields=["name", "employee_name", "company_email", "personal_email"],
	)

	for employee in employees:
		parties.append(
			{
				"party_type": "Employee",
				"party": employee.name,
				"party_name": employee.employee_name,
				"primary_email": employee.company_email or employee.personal_email,
			}
		)

	return parties


def fetch_generic_parties(doc, party_type, collection_type, collection_name):
	"""Generic party fetching for other party types"""
	# This is a placeholder for extensibility
	# Can be enhanced based on specific party type requirements
	return []


@frappe.whitelist()
def get_party_types():
	"""Get list of party types (doctypes with is_party enabled)"""
	# This query filter would be used in the Link field
	# Returns party-enabled doctypes
	return {"filters": [["DocType", "issingle", "=", 0], ["DocType", "istable", "=", 0]]}
