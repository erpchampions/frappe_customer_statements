// Copyright (c) 2025, Cecypo.Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Process Statement of Accounts', {
	refresh: function(frm) {
		// Handle field visibility based on enable_multi_party_type flag
		toggle_field_visibility(frm);
	},

	enable_multi_party_type: function(frm) {
		// Toggle field visibility when flag changes
		toggle_field_visibility(frm);

		// Clear parties table when disabling multi-party mode
		if (!frm.doc.enable_multi_party_type) {
			frm.clear_table('parties');
			frm.refresh_field('parties');
		}

		// Set default party type to Customer when enabling
		if (frm.doc.enable_multi_party_type && !frm.doc.party_type) {
			frm.set_value('party_type', 'Customer');
		}
	},

	party_type: function(frm) {
		// Update party_collection options based on party_type
		update_party_collection_options(frm);

		// Clear existing data
		frm.set_value('party_collection', '');
		frm.set_value('party_collection_name', '');
		frm.clear_table('parties');
		frm.refresh_field('parties');

		// Update party_type in all party rows
		if (frm.doc.parties) {
			frm.doc.parties.forEach(row => {
				frappe.model.set_value(row.doctype, row.name, 'party_type', frm.doc.party_type);
			});
		}
	},

	party_collection: function(frm) {
		// Clear collection name when collection type changes
		frm.set_value('party_collection_name', '');
	},

	fetch_parties: function(frm) {
		// Call server-side method to fetch parties
		if (!frm.doc.party_type) {
			frappe.msgprint(__('Please select Party Type first'));
			return;
		}

		if (!frm.doc.party_collection || !frm.doc.collection_name) {
			frappe.msgprint(__('Please select Fetch Parties By and Collection Name'));
			return;
		}

		frappe.call({
			method: 'customer_statements.custom.process_statement_of_accounts.fetch_parties',
			args: {
				docname: frm.doc.name
			},
			callback: function(r) {
				frm.reload_doc();
			}
		});
	}
});

function toggle_field_visibility(frm) {
	const multi_party_enabled = frm.doc.enable_multi_party_type;

	// Fields to hide when multi-party mode is enabled
	const customer_only_fields = [
		'customer_collection',
		'collection_name',
		'customers',
		'territory',
		'sales_partner',
		'sales_person'
	];

	// Hide/show based on mode
	customer_only_fields.forEach(field => {
		if (frm.fields_dict[field]) {
			frm.toggle_display(field, !multi_party_enabled);

			// Make non-mandatory when hidden
			if (multi_party_enabled) {
				frm.set_df_property(field, 'reqd', 0);
			}
		}
	});

	// Show/hide fetch_customers button
	if (multi_party_enabled) {
		// Hide the original "Fetch Customers" button if it exists
		frm.page.remove_inner_button('Fetch Customers');
	}

	// Update labels based on mode
	if (multi_party_enabled) {
		// Update section labels if needed
		update_dynamic_labels(frm);
	}
}

function update_party_collection_options(frm) {
	const party_type = frm.doc.party_type;

	if (!party_type) {
		return;
	}

	// Define collection options for each party type
	const collection_options_map = {
		'Customer': ['Customer Group', 'Territory', 'Sales Partner', 'Sales Person'],
		'Supplier': ['Supplier Group', 'Supplier Type'],
		'Employee': ['Department', 'Branch', 'Employment Type'],
		'Shareholder': ['Shareholder Type'],
		'Member': ['Member Type']
	};

	const options = collection_options_map[party_type] || [];

	// Set options for party_collection field
	frm.set_df_property('party_collection', 'options', options.join('\n'));

	// Refresh field to show new options
	frm.refresh_field('party_collection');
}

function update_dynamic_labels(frm) {
	// Update labels to be party-agnostic when multi-party mode is enabled
	const party_type = frm.doc.party_type || 'Party';

	// You can add more dynamic label updates here if needed
	// For example, updating section headings, etc.
}

// Child table events for Process Statement of Accounts Party
frappe.ui.form.on('Process Statement of Accounts Party', {
	party: function(frm, cdt, cdn) {
		// Auto-fetch party name and email when party is selected
		const row = frappe.get_doc(cdt, cdn);

		if (row.party && row.party_type) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: row.party_type,
					name: row.party
				},
				callback: function(r) {
					if (r.message) {
						const party_doc = r.message;

						// Get party name based on party type
						let party_name = party_doc.name;
						if (row.party_type === 'Customer' && party_doc.customer_name) {
							party_name = party_doc.customer_name;
						} else if (row.party_type === 'Supplier' && party_doc.supplier_name) {
							party_name = party_doc.supplier_name;
						} else if (row.party_type === 'Employee' && party_doc.employee_name) {
							party_name = party_doc.employee_name;
						}

						frappe.model.set_value(cdt, cdn, 'party_name', party_name);

						// Get primary email
						let primary_email = party_doc.email_id || party_doc.email || party_doc.company_email;
						if (primary_email) {
							frappe.model.set_value(cdt, cdn, 'primary_email', primary_email);
						}
					}
				}
			});
		}
	},

	parties_add: function(frm, cdt, cdn) {
		// Set party_type from parent when adding new row
		const row = frappe.get_doc(cdt, cdn);
		if (frm.doc.party_type) {
			frappe.model.set_value(cdt, cdn, 'party_type', frm.doc.party_type);
		}
	}
});
