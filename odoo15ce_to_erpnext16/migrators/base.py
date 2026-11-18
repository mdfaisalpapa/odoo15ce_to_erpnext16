# Copyright (c) 2026, Mohammed Faisal and contributors
# For license information, please see license.txt

import xmlrpc.client
import frappe

class OdooClient:
	def __init__(self):
		settings = frappe.get_single("Odoo Migration Settings")
		self.url = (settings.odoo_url or "").strip().rstrip("/")
		self.db = (settings.odoo_db or "").strip()
		self.username = (settings.odoo_username or "").strip()
		self.password = settings.get_password("odoo_password")
		self.company = settings.company
		self.batch_size = int(settings.batch_size or 100)
		self.dry_run = bool(settings.dry_run)
		self.settings = settings

		if not all([self.url, self.db, self.username, self.password]):
			frappe.throw("Odoo Migration Settings are incomplete. Please set URL, DB, Username, and Password.")

		self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
		self.uid = self.common.authenticate(self.db, self.username, self.password, {})
		if not self.uid:
			frappe.throw("Failed to authenticate with Odoo using saved credentials.")

		self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)

	def search_count(self, model, domain=None):
		domain = domain or []
		return self.models.execute_kw(self.db, self.uid, self.password, model, "search_count", [domain])

	def search_read(self, model, domain=None, fields=None, offset=0, limit=100, order=None):
		domain = domain or []
		fields = fields or []
		kw = {"offset": offset, "limit": limit}
		if fields:
			kw["fields"] = fields
		if order:
			kw["order"] = order
		return self.models.execute_kw(self.db, self.uid, self.password, model, "search_read", [domain], kw)

	def log_sync(self, model, odoo_id, odoo_name, doctype, docname, status="Success", error=None, payload=None):
		frappe.get_doc({
			"doctype": "Odoo Migration Log",
			"odoo_model": model,
			"odoo_record_id": odoo_id,
			"odoo_record_name": str(odoo_name or "")[:140],
			"erpnext_doctype": doctype,
			"erpnext_docname": docname,
			"status": status,
			"error_message": str(error or ""),
			"request_payload": frappe.as_json(payload) if payload else ""
		}).insert(ignore_permissions=True)
