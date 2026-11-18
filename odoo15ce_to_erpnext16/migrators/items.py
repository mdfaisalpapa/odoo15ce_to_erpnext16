# Copyright (c) 2026, Mohammed Faisal and contributors
# For license information, please see license.txt

import frappe
from odoo15ce_to_erpnext16.migrators.base import OdooClient

def sync_uoms():
	client = OdooClient()
	uoms = client.search_read("uom.uom", fields=["id", "name"])
	created = 0
	for u in uoms:
		uom_name = u["name"].strip()
		if not frappe.db.exists("UOM", uom_name):
			doc = frappe.get_doc({
				"doctype": "UOM",
				"uom_name": uom_name,
				"custom_odoo_id": u["id"]
			})
			doc.insert(ignore_permissions=True)
			created += 1
			client.log_sync("uom.uom", u["id"], uom_name, "UOM", uom_name, "Success")
	return f"UOMs processed. Newly created: {created}"

def sync_categories():
	client = OdooClient()
	cats = client.search_read("product.category", fields=["id", "name", "parent_id"])
	created = 0
	for c in cats:
		group_name = c["name"].strip()
		parent_group = c["parent_id"][1].strip() if c["parent_id"] else "All Item Groups"

		if not frappe.db.exists("Item Group", parent_group):
			parent_group = "All Item Groups"

		if not frappe.db.exists("Item Group", group_name):
			doc = frappe.get_doc({
				"doctype": "Item Group",
				"item_group_name": group_name,
				"parent_item_group": parent_group,
				"is_group": 0
			})
			doc.insert(ignore_permissions=True)
			created += 1
			client.log_sync("product.category", c["id"], group_name, "Item Group", group_name, "Success")
	return f"Item Groups processed. Newly created: {created}"

def sync_items(batch_size=100, limit=None):
	client = OdooClient()
	total = client.search_count("product.product")
	count = limit or total
	offset = 0

	processed = 0
	while offset < count:
		batch = client.search_read("product.product", fields=["id", "name", "default_code", "categ_id", "uom_id", "list_price", "type"], offset=offset, limit=batch_size)
		if not batch:
			break

		for p in batch:
			item_code = (p["default_code"] or f"ITEM-{p['id']}").strip()
			item_name = p["name"].strip()
			item_group = p["categ_id"][1].strip() if p["categ_id"] else "All Item Groups"
			uom = p["uom_id"][1].strip() if p["uom_id"] else "Unit"

			if not frappe.db.exists("Item Group", item_group):
				item_group = "All Item Groups"
			if not frappe.db.exists("UOM", uom):
				uom = "Nos" if frappe.db.exists("UOM", "Nos") else "Unit"

			is_stock = 1 if p["type"] == "product" else 0

			existing = frappe.db.get_value("Item", {"custom_odoo_id": p["id"]}, "name")
			if not existing:
				existing = frappe.db.get_value("Item", {"item_code": item_code}, "name")

			if not existing:
				item_doc = frappe.get_doc({
					"doctype": "Item",
					"item_code": item_code,
					"item_name": item_name,
					"item_group": item_group,
					"stock_uom": uom,
					"is_stock_item": is_stock,
					"standard_rate": p["list_price"] or 0,
					"custom_odoo_id": p["id"]
				})
				item_doc.insert(ignore_permissions=True)
				client.log_sync("product.product", p["id"], item_name, "Item", item_code, "Success")
			else:
				client.log_sync("product.product", p["id"], item_name, "Item", existing, "Skipped", error="Already exists")
			processed += 1

		offset += batch_size

	return f"Total items processed: {processed}"
