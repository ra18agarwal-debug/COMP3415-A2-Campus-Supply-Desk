
import tempfile
import unittest
from pathlib import Path

from supplydesk.service import OrderService


class ExpressFulfillmentTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.service = OrderService(
            Path(self.temp_dir.name) / "state.json"
        )
        self.items = [{"product_id": "notebook", "quantity": 1}]

    def test_express_always_charges_1200_cents(self):
        quote = self.service.quote("regular", self.items, "express")
        self.assertEqual(quote["delivery_cents"], 1200)
        self.assertEqual(
            quote["total_cents"],
            quote["subtotal_cents"] + 1200,
        )

    def test_express_fee_is_not_discounted(self):
        items = [{"product_id": "notebook", "quantity": 10}]
        quote = self.service.quote("student", items, "express")

        self.assertEqual(quote["delivery_cents"], 1200)
        self.assertEqual(
            quote["total_cents"],
            quote["subtotal_cents"]
            - quote["discount_cents"]
            + 1200,
        )

    def test_express_quote_matches_order(self):
        quote = self.service.quote("regular", self.items, "express")
        order = self.service.place_order("regular", self.items, "express")

        self.assertEqual(order["total_cents"], quote["total_cents"])
        self.assertEqual(order["delivery_cents"], 1200)
        self.assertEqual(order["fulfillment"], "express")

    def test_express_order_persists(self):
        order = self.service.place_order("regular", self.items, "express")
        reopened = OrderService(
            Path(self.temp_dir.name) / "state.json"
        )
        saved = reopened.get_order(order["order_id"])

        self.assertEqual(saved["fulfillment"], "express")
        self.assertEqual(saved["delivery_cents"], 1200)
