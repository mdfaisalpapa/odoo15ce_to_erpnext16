# Copyright (c) 2026, Mohammed Faisal and contributors
# For license information, please see license.txt

from frappe.model.document import Document

class OdooMappingRule(Document):
	def validate(self):
		if not self.target_doctype:
			type_map = {
				"Account": "Account",
				"Tax": "Sales Taxes and Charges Template",
				"Payment Method": "Mode of Payment",
				"Item Group": "Item Group",
				"UOM": "UOM"
			}
			self.target_doctype = type_map.get(self.mapping_type, "Account")
