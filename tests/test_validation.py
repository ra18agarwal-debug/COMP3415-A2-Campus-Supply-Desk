
"""Tests for input validation, pricing boundaries, and order behavior."""

from pathlib import Path
import tempfile
import unittest

from supplydesk.service import OrderService


class ValidationTests(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "state.json"
        self.service = OrderService(self.path)

    def test_invalid_customer_type(self):
        with self.assertRaises(ValueError):
            self.service.quote(
                "visitor",
                [{"product_id": "notebook", "quantity": 1}]
            )

    def test_unknown_product(self):
        with self.assertRaises(ValueError):
            self.service.quote(
                "regular",
                [{"product_id": "laptop", "quantity": 1}]
            )

    def test_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.service.quote(
                "regular",
                [{"product_id": "notebook", "quantity": 0}]
            )

    def test_boolean_quantity_rejected(self):
        with self.assertRaises(ValueError):
            self.service.quote(
                "regular",
                [{"product_id": "notebook", "quantity": True}]
            )

    def test_insufficient_stock(self):
        with self.assertRaises(ValueError):
            self.service.place_order(
                "regular",
                [{"product_id": "hoodie", "quantity": 6}]
            )

    def test_empty_items(self):
        with self.assertRaises(ValueError):
            self.service.quote("regular", [])

    def test_free_delivery_threshold(self):
        quote = self.service.quote(
            "regular",
            [{"product_id": "hoodie", "quantity": 3}],
            "delivery"
        )
        self.assertEqual(quote["delivery_cents"], 0)
        self.assertEqual(quote["total_cents"], 12000)

    def test_quote_does_not_change_stock(self):
        before = self.service.catalog()

        self.service.quote(
            "regular",
            [{"product_id": "notebook", "quantity": 2}]
        )

        self.assertEqual(self.service.catalog(), before)
        self.assertFalse(self.path.exists())

    def test_order_ids_increase(self):
        first = self.service.place_order(
            "regular",
            [{"product_id": "notebook", "quantity": 1}]
        )
        second = self.service.place_order(
            "regular",
            [{"product_id": "notebook", "quantity": 1}]
        )

        self.assertEqual(first["order_id"], "ORD-0001")
        self.assertEqual(second["order_id"], "ORD-0002")

    def test_quote_matches_placed_order(self):
        items = [{"product_id": "hoodie", "quantity": 2}]

        quote = self.service.quote("student", items, "delivery")
        order = self.service.place_order("student", items, "delivery")

        for key in (
            "items",
            "subtotal_cents",
            "discount_cents",
            "delivery_cents",
            "total_cents"
        ):
            self.assertEqual(quote[key], order[key])


if __name__ == "__main__":
    unittest.main()
