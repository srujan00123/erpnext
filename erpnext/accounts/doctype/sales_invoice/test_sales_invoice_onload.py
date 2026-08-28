from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from erpnext.controllers.selling_controller import SellingController


class TestSalesInvoiceOnload(FrappeTestCase):
	def test_tolerates_missing_customer(self):
		"""Legacy/orphan invoices remain readable when their Customer is gone."""
		invoice = frappe.get_doc({"doctype": "Sales Invoice", "customer": "missing-customer"})
		with (
			patch.object(SellingController, "onload"),
			patch("frappe.get_cached_value", return_value=None),
		):
			invoice.onload()

		self.assertFalse(invoice.get_onload().get("apply_tds"))
