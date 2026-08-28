"""Regression coverage for Frappe v17's per-module sidebar contract."""

import json
from pathlib import Path

from frappe.desk.doctype.sidebar.convert_fixtures import convert_app, export_path
from frappe.tests import IntegrationTestCase


class TestNativeSidebars(IntegrationTestCase):
	def test_erpnext_ships_the_dock_that_reaches_its_native_sidebars(self):
		dock_path = Path(__file__).resolve().parents[1] / "dock" / "erpnext" / "erpnext.json"
		with dock_path.open() as dock_file:
			dock = json.load(dock_file)

		self.assertEqual(dock["doctype"], "Dock")
		self.assertEqual(dock["app"], "erpnext")
		self.assertEqual(dock["name"], "erpnext")
		self.assertEqual(dock["standard"], 1)
		self.assertEqual(
			[item["link_to"] for item in dock["items"]],
			["Accounts", "Selling", "Buying", "Stock", "Manufacturing", "Projects", "Support", "Setup"],
		)
		self.assertTrue(all(item["link_type"] == "Sidebar" for item in dock["items"]))

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
