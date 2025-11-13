# Copyright (c) 2025, Cecypo.Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, today
from erpnext import get_company_currency


class MultiPartyStatement(Document):
	def validate(self):
		"""Validate the document before saving"""
		if self.from_date and self.to_date:
			if getdate(self.from_date) > getdate(self.to_date):
				frappe.throw(_("From Date cannot be after To Date"))

		if not self.parties:
			frappe.throw(_("Please add at least one party"))

	def before_submit(self):
		"""Generate and send statements before submitting"""
		self.send_statements()

	def send_statements(self):
		"""Generate and send/print statements for all parties"""
		for party in self.parties:
			self.send_single_statement(party)

	def send_single_statement(self, party_row):
		"""Generate statement for a single party"""
		# Get statement data
		statement_dict = self.get_statement_dict(party_row)

		if not statement_dict:
			frappe.msgprint(_("No data found for {0}").format(party_row.party_name))
			return

		# Send email or create PDF based on settings
		if self.enable_auto_email:
			self.send_statement_email(party_row, statement_dict)
		else:
			# For manual process, statements will be printed
			pass

	def get_statement_dict(self, party_row):
		"""Generate statement data for a party"""
		filters = self.get_report_filters(party_row)

		# Get the appropriate report
		if self.report == "General Ledger":
			from erpnext.accounts.report.general_ledger.general_ledger import execute
		elif self.report == "Accounts Receivable":
			from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute
		else:
			frappe.throw(_("Invalid report type"))

		# Execute report
		columns, data = execute(filters)

		if not data:
			return None

		statement_dict = frappe._dict({
			"party": party_row.party,
			"party_name": party_row.party_name,
			"party_type": party_row.party_type,
			"billing_email": party_row.billing_email or party_row.primary_email,
			"data": data,
			"columns": columns,
			"filters": filters
		})

		# Add ageing if required
		if self.include_ageing:
			statement_dict["ageing"] = self.get_ageing_data(party_row)

		return statement_dict

	def get_report_filters(self, party_row):
		"""Generate filters for the report"""
		filters = frappe._dict({
			"company": self.company,
			"from_date": self.from_date,
			"to_date": self.to_date,
			"party_type": party_row.party_type,
			"party": [party_row.party],
			"group_by": "",
		})

		# Add optional filters
		if self.account:
			filters["account"] = self.account

		if self.cost_center:
			filters["cost_center"] = self.cost_center

		if self.project:
			filters["project"] = self.project

		if self.currency:
			filters["presentation_currency"] = self.currency

		# Report-specific filters
		if self.report == "General Ledger":
			filters["show_cancelled_entries"] = 0
			if self.ignore_exchange_rate_revaluation_journals:
				filters["ignore_err"] = 1

		elif self.report == "Accounts Receivable":
			filters["ageing_based_on"] = self.ageing_based_on
			filters["report_date"] = self.posting_date
			filters["range1"] = 30
			filters["range2"] = 60
			filters["range3"] = 90
			filters["range4"] = 120

			if self.based_on_payment_terms:
				filters["based_on_payment_terms"] = 1

		return filters

	def get_ageing_data(self, party_row):
		"""Get ageing data for a party"""
		from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import execute

		filters = frappe._dict({
			"company": self.company,
			"report_date": self.to_date,
			"ageing_based_on": self.ageing_based_on,
			"range1": 30,
			"range2": 60,
			"range3": 90,
			"range4": 120,
			"party_type": party_row.party_type,
			"party": [party_row.party]
		})

		columns, data = execute(filters)
		return data[0] if data else None

	def send_statement_email(self, party_row, statement_dict):
		"""Send statement via email"""
		if not party_row.billing_email and not party_row.primary_email:
			if self.primary_mandatory:
				frappe.msgprint(_("Email not found for {0}, skipping").format(party_row.party_name))
				return

		email = party_row.billing_email or party_row.primary_email

		# Generate PDF
		pdf_content = self.get_statement_pdf(statement_dict)

		# Send email
		frappe.sendmail(
			recipients=[email],
			cc=self.get_cc_emails(),
			subject=_("Statement of Accounts from {0}").format(self.company),
			message=self.get_email_message(party_row),
			attachments=[{
				"fname": f"Statement_{party_row.party}.pdf",
				"fcontent": pdf_content
			}]
		)

	def get_cc_emails(self):
		"""Get CC email addresses"""
		return [row.email for row in self.cc_to if row.email]

	def get_email_message(self, party_row):
		"""Get email message body"""
		return _("""
		<p>Dear {0},</p>
		<p>Please find attached Statement of Accounts for the period from {1} to {2}.</p>
		<p>Best Regards,<br>{3}</p>
		""").format(
			party_row.party_name,
			frappe.format(self.from_date, "Date"),
			frappe.format(self.to_date, "Date"),
			self.company
		)

	def get_statement_pdf(self, statement_dict):
		"""Generate PDF for statement"""
		# This would use the template system to generate PDF
		# For now, return placeholder
		return b"PDF content"


@frappe.whitelist()
def fetch_parties(docname):
	"""Fetch parties based on party_type and collection criteria"""
	doc = frappe.get_doc("Multi Party Statement", docname)

	if not doc.party_type:
		frappe.throw(_("Please select Party Type"))

	party_type = doc.party_type
	collection_type = doc.get("party_collection")
	collection_name = doc.get("party_collection_name")

	# Clear existing parties
	doc.parties = []

	# Fetch parties based on party type
	parties = get_parties(party_type, collection_type, collection_name, doc.company)

	# Add parties to document
	for party_data in parties:
		doc.append("parties", party_data)

	doc.save()
	frappe.msgprint(_("Fetched {0} {1}(s)").format(len(parties), party_type))


def get_parties(party_type, collection_type=None, collection_name=None, company=None):
	"""Get list of parties based on filters"""
	parties = []

	# Build query based on party type
	if party_type == "Customer":
		parties = get_customers(collection_type, collection_name, company)
	elif party_type == "Supplier":
		parties = get_suppliers(collection_type, collection_name, company)
	elif party_type == "Employee":
		parties = get_employees(collection_type, collection_name, company)
	else:
		parties = get_generic_parties(party_type, collection_type, collection_name)

	return parties


def get_customers(collection_type, collection_name, company):
	"""Fetch customers based on collection type"""
	filters = {"disabled": 0}

	if company:
		filters["company"] = company

	if collection_type and collection_name:
		if collection_type == "Customer Group":
			filters["customer_group"] = collection_name
		elif collection_type == "Territory":
			filters["territory"] = collection_name
		elif collection_type == "Sales Partner":
			filters["default_sales_partner"] = collection_name
		elif collection_type == "Sales Person":
			# Need to get customers linked to sales person
			return get_customers_by_sales_person(collection_name, company)

	customers = frappe.get_all(
		"Customer",
		filters=filters,
		fields=["name", "customer_name", "email_id"]
	)

	return [{
		"party_type": "Customer",
		"party": c.name,
		"party_name": c.customer_name or c.name,
		"primary_email": c.email_id
	} for c in customers]


def get_customers_by_sales_person(sales_person, company):
	"""Get customers linked to a sales person"""
	customers = frappe.db.sql("""
		SELECT DISTINCT c.name, c.customer_name, c.email_id
		FROM `tabCustomer` c
		INNER JOIN `tabSales Team` st ON st.parent = c.name AND st.parenttype = 'Customer'
		WHERE st.sales_person = %s AND c.disabled = 0
		{company_condition}
	""".format(
		company_condition="AND c.company = %(company)s" if company else ""
	), {"sales_person": sales_person, "company": company}, as_dict=1)

	return [{
		"party_type": "Customer",
		"party": c.name,
		"party_name": c.customer_name or c.name,
		"primary_email": c.email_id
	} for c in customers]


def get_suppliers(collection_type, collection_name, company):
	"""Fetch suppliers based on collection type"""
	filters = {"disabled": 0}

	if collection_type and collection_name:
		if collection_type == "Supplier Group":
			filters["supplier_group"] = collection_name
		elif collection_type == "Supplier Type":
			filters["supplier_type"] = collection_name

	suppliers = frappe.get_all(
		"Supplier",
		filters=filters,
		fields=["name", "supplier_name", "email_id"]
	)

	return [{
		"party_type": "Supplier",
		"party": s.name,
		"party_name": s.supplier_name or s.name,
		"primary_email": s.email_id
	} for s in suppliers]


def get_employees(collection_type, collection_name, company):
	"""Fetch employees based on collection type"""
	filters = {"status": "Active"}

	if company:
		filters["company"] = company

	if collection_type and collection_name:
		if collection_type == "Department":
			filters["department"] = collection_name
		elif collection_type == "Branch":
			filters["branch"] = collection_name
		elif collection_type == "Employment Type":
			filters["employment_type"] = collection_name

	employees = frappe.get_all(
		"Employee",
		filters=filters,
		fields=["name", "employee_name", "prefered_email", "company_email", "personal_email"]
	)

	return [{
		"party_type": "Employee",
		"party": e.name,
		"party_name": e.employee_name or e.name,
		"primary_email": e.prefered_email or e.company_email or e.personal_email
	} for e in employees]


def get_generic_parties(party_type, collection_type, collection_name):
	"""Fetch generic party types"""
	try:
		parties = frappe.get_all(
			party_type,
			filters={},
			fields=["name"]
		)

		return [{
			"party_type": party_type,
			"party": p.name,
			"party_name": p.name,
			"primary_email": ""
		} for p in parties]
	except Exception as e:
		frappe.throw(_("Error fetching {0}: {1}").format(party_type, str(e)))
