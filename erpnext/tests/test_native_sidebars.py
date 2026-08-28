"""Regression coverage for Frappe v17's per-module sidebar contract."""

import json

from frappe.desk.doctype.sidebar.convert_fixtures import convert_app, export_path
from frappe.tests import IntegrationTestCase


class TestNativeSidebars(IntegrationTestCase):
	def test_every_legacy_erpnext_sidebar_module_has_been_converted(self):
		results = convert_app("erpnext", dry_run=True)
		unconverted = [result for result in results if result["state"] != "already converted"]
		self.assertEqual(unconverted, [])

	def test_accounts_sidebar_contains_the_billing_routes(self):
		with open(export_path("Accounts", "Accounts")) as sidebar_file:  # nosemgrep
			sidebar = json.load(sidebar_file)

		self.assertEqual(sidebar["doctype"], "Sidebar")
		self.assertEqual(sidebar["module"], "Accounts")
		links = {item.get("link_to") for item in sidebar["items"]}
		self.assertIn("Sales Invoice", links)
		self.assertIn("Payment Entry", links)
