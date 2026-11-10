from pathlib import Path
import tempfile
import unittest

from supplydesk.service import OrderService


class KnownDefectTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.service = OrderService(
            Path(self.directory.name) / "state.json"
        )

    def test_student_discount_at_exactly_50_dollars(self):
        quote = self.service.quote(
            "student",
            [{"product_id": "bag", "quantity": 2}]
        )
        self.assertEqual(quote["subtotal_cents"], 5000)
        self.assertEqual(quote["discount_cents"], 500)
        self.assertEqual(quote["total_cents"], 4500)

    def test_cancelling_twice_does_not_restore_stock_twice(self):
        order = self.service.place_order(
            "regular",
            [{"product_id": "notebook", "quantity": 2}]
        )

        self.service.cancel_order(order["order_id"])
        stock_after_first_cancel = self.service.catalog()

        self.service.cancel_order(order["order_id"])
        stock_after_second_cancel = self.service.catalog()

        self.assertEqual(
            stock_after_second_cancel,
            stock_after_first_cancel
        )


if __name__ == "__main__":
    unittest.main()