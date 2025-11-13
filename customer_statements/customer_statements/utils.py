# Copyright (c) 2025, Cecypo.Tech and contributors
# For license information, please see license.txt

import frappe


def get_signature_settings():
	"""
	Get signature section configuration from Customer Statements Settings.
	Returns a dictionary with settings for rendering signature sections in reports.
	"""
	try:
		settings = frappe.get_single("Customer Statements Settings")

		return {
			"enabled": settings.get("enable_signature_section", 0),
			"prepared_by_label": settings.get("signature_label_prepared_by", "Prepared By"),
			"reviewed_by_label": settings.get("signature_label_reviewed_by", "Reviewed By"),
			"approved_by_label": settings.get("signature_label_approved_by", "Approved By"),
			"show_name_field": settings.get("signature_show_name_field", 1),
			"show_date_field": settings.get("signature_show_date_field", 1),
		}
	except Exception:
		# Return default settings if document doesn't exist yet
		return {
			"enabled": 0,
			"prepared_by_label": "Prepared By",
			"reviewed_by_label": "Reviewed By",
			"approved_by_label": "Approved By",
			"show_name_field": 1,
			"show_date_field": 1,
		}


def jinja_methods():
	"""
	Methods to be exposed to Jinja templates.
	"""
	return {
		"get_signature_settings": get_signature_settings,
	}
