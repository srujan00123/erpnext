import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(
  new URL("./pos_past_order_summary.js", import.meta.url),
  "utf8",
);

function loadSummaryPrototype(frappe) {
  const context = vm.createContext({ erpnext: { PointOfSale: {} }, frappe });
  vm.runInContext(source, context);
  return context.erpnext.PointOfSale.PastOrderSummary.prototype;
}

test("Print Receipt resolves the format from the saved invoice POS Profile", async () => {
  const printed = [];
  const frappe = {
    db: {
      get_value: async (doctype, name, fieldname) => {
        assert.equal(doctype, "POS Profile");
        assert.equal(name, "Pharmacy POS - TP");
        assert.equal(fieldname, "print_format");
        return { message: { print_format: "Hospital Pharmacy Invoice" } };
      },
    },
    utils: { print: (...args) => printed.push(args) },
    boot: { lang: "en" },
  };
  const summary = Object.create(loadSummaryPrototype(frappe));
  summary.events = {
    get_frm: () => ({ pos_print_format: "Hospital Invoice" }),
  };
  summary.doc = {
    doctype: "Sales Invoice",
    name: "TP-INV-TEST",
    pos_profile: "Pharmacy POS - TP",
    letter_head: null,
    language: "en",
  };

  await summary.print_receipt();

  assert.deepEqual(printed, [
    ["Sales Invoice", "TP-INV-TEST", "Hospital Pharmacy Invoice", null, "en"],
  ]);
});

test("Print Receipt keeps the form format fallback for a receipt without a POS Profile", async () => {
  const printed = [];
  const frappe = {
    db: { get_value: async () => assert.fail("profile lookup must not run") },
    utils: { print: (...args) => printed.push(args) },
    boot: { lang: "en" },
  };
  const summary = Object.create(loadSummaryPrototype(frappe));
  summary.events = {
    get_frm: () => ({ pos_print_format: "Fallback Receipt" }),
  };
  summary.doc = {
    doctype: "Sales Invoice",
    name: "SINV-TEST",
    letter_head: null,
  };

  await summary.print_receipt();

  assert.equal(printed[0][2], "Fallback Receipt");
});
