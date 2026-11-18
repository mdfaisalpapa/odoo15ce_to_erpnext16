# Copyright (c) 2026, Mohammed Faisal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import xmlrpc.client

class OdooMigrationSettings(Document):
	@frappe.whitelist()
	def test_connection(self):
		url = (self.odoo_url or "").strip().rstrip("/")
		db = (self.odoo_db or "").strip()
		username = (self.odoo_username or "").strip()
		password = self.get_password("odoo_password")

		if not all([url, db, username, password]):
			frappe.throw("Please provide Odoo Server URL, Database Name, Username, and Password.")

		try:
			common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
			uid = common.authenticate(db, username, password, {})
			if uid:
				self.status = "Connected"
				self.save()
				return {"status": "success", "message": f"Successfully connected to Odoo 15! Authenticated UID: {uid}"}
			else:
				frappe.throw("Authentication failed. Check your Odoo username and password.")
		except Exception as e:
			frappe.throw(f"Connection error: {str(e)}")
