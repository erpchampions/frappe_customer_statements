# Copyright (c) 2025, Cecypo.Tech and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Migration patch to create custom fields for multi-party type support"""
	from customer_statements.install import create_custom_fields

	create_custom_fields()
