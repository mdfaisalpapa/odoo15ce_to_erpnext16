# Copyright (c) 2026, Mohammed Faisal and contributors
# For license information, please see license.txt

import frappe
from odoo15ce_to_erpnext16.migrators.base import OdooClient

def sync_partners(batch_size=50, limit=None, include_inactive=True):
	client = OdooClient()
	domains = [[("active", "=", True)]]
	if include_inactive:
		domains.append([("active", "=", False)])

	processed = 0
	for domain in domains:
		total = client.search_count("res.partner", domain=domain)
		count = limit or total
		offset = 0

		while offset < count:
			batch = client.search_read(
				"res.partner",
				domain=domain,
				fields=["id", "name", "ref", "email", "phone", "mobile", "vat", "customer_rank", "supplier_rank", "is_company", "active"],
				offset=offset,
				limit=batch_size
			)
			if not batch:
				break

			for p in batch:
				partner_name = (p["name"] or f"Partner-{p['id']}").strip()
				is_customer = (p.get("customer_rank") or 0) > 0 or not ((p.get("supplier_rank") or 0) > 0)
				is_supplier = (p.get("supplier_rank") or 0) > 0

				# Sync Customer
				if is_customer:
					# 1. Primary lookup by immutable Odoo partner ID
					existing = frappe.db.get_value("Customer", {"custom_odoo_id": p["id"]}, "name")
					ref_val = str(p.get("ref") or "").strip()

					# 2. If not found by custom_odoo_id, check if existing customer matches ref
					if not existing and ref_val:
						existing_by_ref = frappe.db.get_value("Customer", {"name": ref_val}, "name")
						if existing_by_ref:
							if not client.dry_run:
								frappe.db.set_value("Customer", existing_by_ref, {
									"custom_odoo_id": p["id"],
									"custom_odoo_ref": ref_val
								})
							existing = existing_by_ref
							client.log_sync("res.partner", p["id"], partner_name, "Customer", existing, "Success", error="Linked by ref to existing Customer (Dry Run)" if client.dry_run else "Linked by ref to existing Customer")

					if not existing:
						naming_strategy = getattr(client.settings, "customer_naming_strategy", "Match/Set to Odoo Ref (Fallback to Auto-naming)")
						cust_group = getattr(client.settings, "default_customer_group", None) or "Non Member"

						c_doc = frappe.new_doc("Customer")
						c_doc.customer_name = partner_name
						c_doc.customer_type = "Company" if p.get("is_company") else "Individual"
						c_doc.customer_group = cust_group
						c_doc.territory = "All Territories"
						c_doc.custom_odoo_id = p["id"]
						c_doc.custom_odoo_ref = ref_val
						if not p.get("active", True):
							c_doc.disabled = 1

						# Handle naming strategy
						if naming_strategy == "Match/Set to Odoo Ref (Fallback to Auto-naming)" and ref_val:
							if not frappe.db.exists("Customer", ref_val):
								c_doc.name = ref_val
						elif naming_strategy == "Set to Odoo ID":
							odoo_id_name = f"ODOO-{p['id']}"
							if not frappe.db.exists("Customer", odoo_id_name):
								c_doc.name = odoo_id_name

						if not client.dry_run:
							c_doc.insert(ignore_permissions=True)
							client.log_sync("res.partner", p["id"], partner_name, "Customer", c_doc.name, "Success")
							# Trigger optional custom hook for downstream apps
							for hook in frappe.get_hooks("on_odoo_partner_migrated"):
								frappe.get_attr(hook)(partner=p, customer=c_doc)
						else:
							target_name = c_doc.name or f"New Customer ({partner_name})"
							client.log_sync("res.partner", p["id"], partner_name, "Customer", target_name, "Dry Run", error="Would create new Customer")
					elif existing and not client.dry_run:
						# If already linked but ref wasn't set, keep it synchronized
						if ref_val and not frappe.db.get_value("Customer", existing, "custom_odoo_ref"):
							frappe.db.set_value("Customer", existing, "custom_odoo_ref", ref_val)
						client.log_sync("res.partner", p["id"], partner_name, "Customer", existing, "Skipped", error="Already exists")

				# Sync Supplier
				if is_supplier:
					existing_sup = frappe.db.get_value("Supplier", {"custom_odoo_id": p["id"]}, "name")
					if not existing_sup:
						# Check if matching supplier exists by name
						existing_by_name = frappe.db.get_value("Supplier", {"name": partner_name}, "name") or frappe.db.get_value("Supplier", {"supplier_name": partner_name}, "name")
						if existing_by_name:
							if not client.dry_run:
								frappe.db.set_value("Supplier", existing_by_name, "custom_odoo_id", p["id"])
							existing_sup = existing_by_name
							client.log_sync("res.partner", p["id"], partner_name, "Supplier", existing_sup, "Success", error="Linked to existing Supplier by name")
						else:
							default_sup_group = "Local" if frappe.db.exists("Supplier Group", "Local") else (frappe.db.get_value("Supplier Group", {"is_group": 0}, "name") or "All Supplier Groups")
							s_doc = frappe.get_doc({
								"doctype": "Supplier",
								"supplier_name": partner_name,
								"supplier_type": "Company" if p.get("is_company") else "Individual",
								"supplier_group": default_sup_group,
								"custom_odoo_id": p["id"]
							})
							if not client.dry_run:
								s_doc.insert(ignore_permissions=True)
								client.log_sync("res.partner", p["id"], partner_name, "Supplier", s_doc.name, "Success")
							else:
								client.log_sync("res.partner", p["id"], partner_name, "Supplier", f"New Supplier ({partner_name})", "Dry Run", error="Would create new Supplier")
					elif not client.dry_run:
						client.log_sync("res.partner", p["id"], partner_name, "Supplier", existing_sup, "Skipped", error="Already exists")

				processed += 1

			if not client.dry_run:
				frappe.db.commit()

			offset += batch_size

	return f"Total partners processed: {processed}"
