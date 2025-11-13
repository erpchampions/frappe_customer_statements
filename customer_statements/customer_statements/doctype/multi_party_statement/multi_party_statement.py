# Copyright (c) 2025, Cecypo.Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, today, get_url
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
		statement_dict = get_statement_dict(self)

		if not statement_dict:
			frappe.msgprint(_("No statements generated"))
			return

		# Send emails if auto-email enabled
		if self.enable_auto_email:
			for party in self.parties:
				if party.party in statement_dict:
					self.send_statement_email(party, statement_dict[party.party])

	def send_statement_email(self, party_row, statement_html):
		"""Send statement via email"""
		from frappe.utils.pdf import get_pdf

		if not party_row.billing_email and not party_row.primary_email:
			if self.primary_mandatory:
				frappe.msgprint(_("Email not found for {0}, skipping").format(party_row.party_name))
				return

		email = party_row.billing_email or party_row.primary_email

		# Generate PDF from HTML
		pdf_content = get_pdf(statement_html, {"orientation": self.orientation})

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


def get_statement_dict(doc, get_statement_dict=False):
	"""
	Generate statement dictionary for all parties.
	Returns: {party_name: HTML_string} if get_statement_dict=False (default)
	         {party_name: [HTML_string, ageing_data]} if get_statement_dict=True

	This follows ERPNext's exact pattern for Process Statement of Accounts.
	"""
	statement_dict = {}

	for party_row in doc.parties:
		# Get presentation currency
		presentation_currency = get_presentation_currency(doc, party_row)

		# Get ageing data if required
		ageing = None
		if doc.include_ageing or (doc.enable_auto_email and doc.filter_duration):
			ageing = get_ageing(doc, party_row, presentation_currency)

		# Build filters based on report type
		if doc.report == "General Ledger":
			filters = get_gl_filters(doc, party_row, presentation_currency)
			columns, res = get_soa(filters)
			# Skip if only header/footer rows (exactly 3 rows = no real transactions)
			if len(res) == 3:
				continue
		elif doc.report == "Accounts Receivable":
			filters = get_ar_filters(doc, party_row, presentation_currency)
			columns, res = get_ar_soa(filters)
			# Skip if no data
			if not res:
				continue
		else:
			continue

		# Generate HTML using ERPNext's template rendering
		html = get_html(doc, party_row, filters, res, columns, ageing, presentation_currency)

		if get_statement_dict:
			statement_dict[party_row.party] = [html, ageing]
		else:
			statement_dict[party_row.party] = html

	return statement_dict


def get_html(doc, party_row, filters, res, columns, ageing, presentation_currency):
	"""
	Render statement HTML using templates.
	Follows ERPNext's exact template rendering pattern with hooks support.
	"""
	# Get template based on report type
	if doc.report == "General Ledger":
		template = "customer_statements/templates/process_statement_of_accounts.html"
	else:
		template = "customer_statements/templates/process_statement_of_accounts_accounts_receivable.html"

	# Check for custom templates via hooks
	hooks = frappe.get_hooks("process_soa_html")
	if hooks and doc.report in hooks:
		custom_templates = hooks[doc.report]
		if custom_templates and len(custom_templates) > 0:
			template = custom_templates[-1]  # Use last registered template

	# Get letterhead
	letter_head = {}
	if doc.letter_head:
		letter_head_doc = frappe.get_doc("Letter Head", doc.letter_head)
		letter_head = {
			"content": letter_head_doc.content if letter_head_doc.content else "",
			"footer": letter_head_doc.footer if letter_head_doc.footer else ""
		}

	# Prepare context for template (matches ERPNext core exactly)
	context = {
		"filters": filters,
		"data": res,
		"report": frappe._dict({
			"report_name": doc.report,
			"columns": columns
		}),
		"ageing": ageing,
		"letter_head": letter_head,
		"terms_and_conditions": "",  # Can be extended
		"age_as_on": doc.posting_date
	}

	# Render template
	html = frappe.render_template(template, context)

	# Wrap in print view base template (same as ERPNext core)
	from frappe.www.printview import get_print_style

	html = frappe.render_template(
		"frappe/www/printview.html",
		{
			"body": html,
			"css": get_print_style(),
			"title": f"Statement For {party_row.party_name}"
		}
	)

	return html


def get_gl_filters(doc, party_row, presentation_currency):
	"""Get filters for General Ledger report - matches ERPNext core exactly"""
	filters = frappe._dict({
		"company": doc.company,
		"from_date": doc.from_date,
		"to_date": doc.to_date,
		"party_type": party_row.party_type,
		"party": [party_row.party],
		"party_name": [party_row.party_name],
		"group_by": "",
		"presentation_currency": presentation_currency,
		"currency": presentation_currency,
		"tax_id": get_party_tax_id(party_row.party_type, party_row.party),
		"show_cancelled_entries": 0,
		"show_opening_entries": 0,  # CRITICAL: Prevents duplicate opening entries
		"include_default_book_entries": 0,  # CRITICAL: Prevents book entry duplicates
		"show_net_values_in_party_account": doc.get("show_net_values_in_party_account", 0),
		"show_remarks": doc.get("show_remarks", 0),
		"categorize_by": doc.get("categorize_by", "Categorize by Voucher (Consolidated)")
	})

	if doc.account:
		filters["account"] = doc.account

	if doc.cost_center:
		filters["cost_center"] = doc.cost_center

	if doc.project:
		filters["project"] = doc.project

	if doc.get("ignore_exchange_rate_revaluation_journals"):
		filters["ignore_err"] = 1

	if doc.get("ignore_cr_dr_notes"):
		filters["ignore_cr_dr_notes"] = 1

	return filters


def get_ar_filters(doc, party_row, presentation_currency):
	"""Get filters for Accounts Receivable report - matches ERPNext core exactly"""
	filters = frappe._dict({
		"company": doc.company,
		"report_date": doc.posting_date,
		"ageing_based_on": doc.ageing_based_on,
		"range1": 30,
		"range2": 60,
		"range3": 90,
		"range4": 120,
		"party_type": party_row.party_type,
		"party": [party_row.party],
		"party_name": [party_row.party_name],
		"presentation_currency": presentation_currency,
		"tax_id": get_party_tax_id(party_row.party_type, party_row.party)
	})

	if doc.account:
		filters["account"] = doc.account

	if doc.cost_center:
		filters["cost_center"] = doc.cost_center

	if doc.project:
		filters["project"] = doc.project

	if doc.get("based_on_payment_terms"):
		filters["based_on_payment_terms"] = 1

	if doc.get("show_net_values_in_party_account"):
		filters["show_net_values_in_party_account"] = 1

	return filters


def get_soa(filters):
	"""Get General Ledger data"""
	from erpnext.accounts.report.general_ledger.general_ledger import execute
	return execute(filters)


def get_ar_soa(filters):
	"""Get Accounts Receivable data"""
	from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute
	return execute(filters)


def get_ageing(doc, party_row, presentation_currency):
	"""Get ageing data for a party"""
	from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import execute

	filters = frappe._dict({
		"company": doc.company,
		"report_date": doc.to_date,
		"ageing_based_on": doc.ageing_based_on,
		"range1": 30,
		"range2": 60,
		"range3": 90,
		"range4": 120,
		"party_type": party_row.party_type,
		"party": [party_row.party],
		"presentation_currency": presentation_currency
	})

	columns, data = execute(filters)
	return data[0] if data else None


def get_party_tax_id(party_type, party):
	"""Get tax ID for a party"""
	if party_type in ["Customer", "Supplier"]:
		return frappe.db.get_value(party_type, party, "tax_id") or ""
	return ""


def get_presentation_currency(doc, party_row):
	"""Get presentation currency for the statement"""
	# Use doc currency if specified, otherwise company currency
	return doc.currency or get_company_currency(doc.company)


@frappe.whitelist()
def get_report_pdf(docname, consolidated=True):
	"""
	Generate PDF report following ERPNext's exact pattern.
	Returns consolidated PDF or dictionary of individual PDFs.
	"""
	from frappe.utils.pdf import get_pdf

	doc = frappe.get_doc("Multi Party Statement", docname)
	statement_dict = get_statement_dict(doc)

	if not statement_dict:
		frappe.throw(
			_("No data found for any parties in the selected date range. Please check your filters and date range.")
		)

	if cint(consolidated):
		# Consolidated PDF with page breaks
		delimiter = '<div style="page-break-before: always;"></div>' if doc.include_break else ""
		result = delimiter.join(list(statement_dict.values()))
		return get_pdf(result, {"orientation": doc.orientation})
	else:
		# Individual PDFs
		for party, statement_html in statement_dict.items():
			statement_dict[party] = get_pdf(statement_html, {"orientation": doc.orientation})
		return statement_dict


@frappe.whitelist()
def get_statements_pdf(docname):
	"""Generate combined PDF for download"""
	import base64

	# get_report_pdf will throw error if no data
	pdf_content = get_report_pdf(docname, consolidated=True)

	# Encode as base64
	pdf_data = base64.b64encode(pdf_content).decode()

	doc = frappe.get_doc("Multi Party Statement", docname)
	return {
		"pdf_data": pdf_data,
		"filename": f"Statements_{doc.name}.pdf"
	}


@frappe.whitelist()
def get_print_html(docname):
	"""Generate combined HTML for printing"""
	doc = frappe.get_doc("Multi Party Statement", docname)
	statement_dict = get_statement_dict(doc)

	if not statement_dict:
		frappe.throw(
			_("No data found for any parties in the selected date range. Please check your filters and date range.")
		)

	# Join all HTML with page breaks
	delimiter = '<div style="page-break-after: always;"></div>' if doc.include_break else ""
	return delimiter.join(list(statement_dict.values()))


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
