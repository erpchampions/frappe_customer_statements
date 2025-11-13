// Copyright (c) 2025, Cecypo.Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Multi Party Statement', {
	onload: function(frm) {
		frm.set_query('party_type', () => {
			return {
				filters: {
					name: ['in', ['Customer', 'Supplier', 'Employee', 'Shareholder', 'Member']]
				}
			};
		});
	},

	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Send Emails'), () => {
				frm.call('send_statements').then(() => {
					frappe.msgprint(__('Statements sent successfully'));
				});
			});

			frm.add_custom_button(__('Download PDF'), () => {
				// Trigger PDF download
				frappe.msgprint(__('PDF download feature coming soon'));
			});
		}
	},

	party_type: function(frm) {
		update_party_collection_options(frm);
		frm.set_value('party_collection', '');
		frm.set_value('party_collection_name', '');
		frm.set_value('parties', []);
	},

	fetch_parties: function(frm) {
		if (!frm.doc.party_type) {
			frappe.msgprint(__('Please select Party Type first'));
			return;
		}

		frappe.call({
			method: 'customer_statements.customer_statements.doctype.multi_party_statement.multi_party_statement.fetch_parties',
			args: {
				docname: frm.doc.name
			},
			callback: function(r) {
				frm.reload_doc();
			}
		});
	},

	company: function(frm) {
		if (frm.doc.company) {
			frappe.db.get_value('Company', frm.doc.company, 'default_currency', (r) => {
				if (r && r.default_currency) {
					frm.set_value('currency', r.default_currency);
				}
			});
		}
	}
});

function update_party_collection_options(frm) {
	const party_type = frm.doc.party_type;

	const collection_options_map = {
		'Customer': ['Customer Group', 'Territory', 'Sales Partner', 'Sales Person'],
		'Supplier': ['Supplier Group', 'Supplier Type'],
		'Employee': ['Department', 'Branch', 'Employment Type'],
	};

	const options = collection_options_map[party_type] || [];

	frm.set_df_property('party_collection', 'options', options.join('\n'));
	frm.refresh_field('party_collection');
}

// Child table events for Process Statement of Accounts Party
frappe.ui.form.on('Process Statement of Accounts Party', {
	party_type: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		row.party = '';
		row.party_name = '';
		row.primary_email = '';
		row.billing_email = '';
		frm.refresh_field('parties');
	},

	party: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.party && row.party_type) {
			// Fetch party details
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: row.party_type,
					name: row.party
				},
				callback: function(r) {
					if (r.message) {
						const party_doc = r.message;

						// Set party name based on party type
						const name_field_map = {
							'Customer': 'customer_name',
							'Supplier': 'supplier_name',
							'Employee': 'employee_name'
						};

						const name_field = name_field_map[row.party_type];
						if (name_field && party_doc[name_field]) {
							frappe.model.set_value(cdt, cdn, 'party_name', party_doc[name_field]);
						} else {
							frappe.model.set_value(cdt, cdn, 'party_name', party_doc.name);
						}

						// Set primary email based on party type
						const email_field_map = {
							'Customer': 'email_id',
							'Supplier': 'email_id',
							'Employee': 'prefered_email'
						};

						const email_field = email_field_map[row.party_type];
						if (email_field && party_doc[email_field]) {
							frappe.model.set_value(cdt, cdn, 'primary_email', party_doc[email_field]);
						} else if (party_doc.company_email) {
							frappe.model.set_value(cdt, cdn, 'primary_email', party_doc.company_email);
						}
					}
				}
			});
		}
	}
});
