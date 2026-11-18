// Copyright (c) 2026, Mohammed Faisal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Odoo Migration Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Test Connection"), () => {
			frm.call("test_connection").then(r => {
				if (r.message && r.message.status === "success") {
					frappe.msgprint({
						title: __("Success"),
						message: __(r.message.message),
						indicator: "green"
					});
					frm.reload_doc();
				}
			});
		});
	}
});
