import unittest
from fulfillment.engine import MultiWarehouseFulfillmentRouter, Warehouse, CartItem


class TestMultiWarehouseFulfillment(unittest.TestCase):
    def setUp(self):
        self.router = MultiWarehouseFulfillmentRouter()
        # Regional DC South (Bangalore)
        self.router.register_warehouse(Warehouse(
            warehouse_id="RDC-BLR",
            name="Bangalore Regional DC",
            warehouse_type="RDC",
            region="SOUTH",
            inventory={"IPHONE-15": 10, "AIRPODS-PRO": 0}
        ))
        # Mother Hub West (Bhiwandi)
        self.router.register_warehouse(Warehouse(
            warehouse_id="HUB-BHIWANDI",
            name="Mumbai Mega Mother Hub",
            warehouse_type="MOTHER_HUB",
            region="WEST",
            inventory={"IPHONE-15": 50, "AIRPODS-PRO": 25}
        ))

    def test_single_warehouse_priority(self):
        # Customer in South ordering 2 iPhone-15 (can be fulfilled entirely by local RDC-BLR)
        cart = [CartItem(sku="IPHONE-15", quantity=2, unit_price=79999.0)]
        plan = self.router.route_order("ORD-1001", dest_region="SOUTH", cart_items=cart)
        self.assertEqual(plan.total_packages, 1)
        self.assertEqual(plan.shipments[0].fulfilling_warehouse_id, "RDC-BLR")
        self.assertEqual(plan.shipments[0].shipping_zone, "REGIONAL")
        self.assertEqual(self.router.warehouses["RDC-BLR"].inventory["IPHONE-15"], 8)

    def test_split_order_allocation(self):
        # Customer in South ordering 1 iPhone-15 and 2 AirPods Pro (AirPods Pro not in BLR, must pull from Mumbai)
        cart = [
            CartItem(sku="IPHONE-15", quantity=1, unit_price=79999.0),
            CartItem(sku="AIRPODS-PRO", quantity=2, unit_price=24999.0)
        ]
        plan = self.router.route_order("ORD-1002", dest_region="SOUTH", cart_items=cart)
        # Note: Mother Hub BHIWANDI has BOTH items (can fulfill all in 1 package with national zone!)
        self.assertEqual(plan.total_packages, 1)
        self.assertEqual(plan.shipments[0].fulfilling_warehouse_id, "HUB-BHIWANDI")
        self.assertEqual(plan.shipments[0].shipping_zone, "NATIONAL")


if __name__ == "__main__":
    unittest.main()
