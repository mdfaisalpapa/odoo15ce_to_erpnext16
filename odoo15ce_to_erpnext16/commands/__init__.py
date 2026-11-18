# Copyright (c) 2026, Mohammed Faisal and contributors
# For license information, please see license.txt

import click
import frappe
from frappe.commands import pass_context

@click.group()
def odoo():
	"""Odoo 15 to ERPNext 16 migration commands."""
	pass

@odoo.command("test-connection")
@pass_context
def test_connection(context):
	"""Test connection to Odoo instance."""
	site = context.sites[0]
	frappe.init(site=site)
	frappe.connect()
	settings = frappe.get_single("Odoo Migration Settings")
	res = settings.test_connection()
	click.echo(res.get("message"))
	frappe.destroy()

@odoo.command("sync-uom")
@pass_context
def sync_uom_cmd(context):
	"""Sync Units of Measure from Odoo."""
	site = context.sites[0]
	frappe.init(site=site)
	frappe.connect()
	from odoo15ce_to_erpnext16.migrators.items import sync_uoms
	res = sync_uoms()
	click.echo(res)
	frappe.destroy()

@odoo.command("sync-categories")
@pass_context
def sync_categories_cmd(context):
	"""Sync Product Categories to Item Groups."""
	site = context.sites[0]
	frappe.init(site=site)
	frappe.connect()
	from odoo15ce_to_erpnext16.migrators.items import sync_categories
	res = sync_categories()
	click.echo(res)
	frappe.destroy()

@odoo.command("sync-items")
@click.option("--limit", default=None, type=int, help="Limit number of items to sync")
@pass_context
def sync_items_cmd(context, limit=None):
	"""Sync Products from Odoo to Items in ERPNext."""
	site = context.sites[0]
	frappe.init(site=site)
	frappe.connect()
	from odoo15ce_to_erpnext16.migrators.items import sync_items
	res = sync_items(limit=limit)
	click.echo(res)
	frappe.destroy()

@odoo.command("sync-partners")
@click.option("--limit", default=None, type=int, help="Limit number of partners to sync")
@pass_context
def sync_partners_cmd(context, limit=None):
	"""Sync res.partner from Odoo to Customers/Suppliers."""
	site = context.sites[0]
	frappe.init(site=site)
	frappe.connect()
	from odoo15ce_to_erpnext16.migrators.partners import sync_partners
	res = sync_partners(limit=limit)
	click.echo(res)
	frappe.destroy()

commands = [odoo]
