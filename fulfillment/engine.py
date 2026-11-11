"""Multi-Warehouse Fulfillment Router, Stock Allocation & Split Shipment Optimizer."""

import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Warehouse(BaseModel):
    warehouse_id: str
    name: str
    warehouse_type: str  # MOTHER_HUB, RDC (Regional DC), FDC (Forward DC)
    region: str          # NORTH, SOUTH, WEST, EAST
    inventory: Dict[str, int] = Field(default_factory=dict)  # sku -> available stock


class CartItem(BaseModel):
    sku: str
    quantity: int
    unit_price: float


class ShipmentPackage(BaseModel):
    shipment_id: str
    fulfilling_warehouse_id: str
    warehouse_name: str
    items: Dict[str, int]  # sku -> allocated qty
    shipping_zone: str     # LOCAL, REGIONAL, NATIONAL
    estimated_freight: float


class FulfillmentPlan(BaseModel):
    order_id: str
    destination_region: str
    total_packages: int
    shipments: List[ShipmentPackage]
    is_partially_unfulfilled: bool = False
    unfulfilled_items: Dict[str, int] = Field(default_factory=dict)
    total_freight_cost: float


class MultiWarehouseFulfillmentRouter:
    """Routes customer orders across national distribution networks minimizing split shipments and transit zones."""

    ZONE_FREIGHT_MATRIX = {
        "LOCAL": 40.0,       # same city / FDC
        "REGIONAL": 75.0,    # same region RDC (e.g. North to North)
        "NATIONAL": 140.0,   # inter-region (e.g. North Mother Hub to South Customer)
    }

    def __init__(self):
        self.warehouses: Dict[str, Warehouse] = {}

    def register_warehouse(self, wh: Warehouse) -> Warehouse:
        self.warehouses[wh.warehouse_id] = wh
        return wh

    def route_order(self, order_id: str, dest_region: str, cart_items: List[CartItem]) -> FulfillmentPlan:
        # Sort warehouses by regional proximity:
        # 1. Local/RDC in same region
        # 2. Mother Hubs
        # 3. Other regional DCs
        def sort_priority(w: Warehouse):
            is_same_region = (w.region == dest_region)
            priority = 0
            if is_same_region and w.warehouse_type == "FDC":
                priority = 1
            elif is_same_region and w.warehouse_type == "RDC":
                priority = 2
            elif w.warehouse_type == "MOTHER_HUB":
                priority = 3
            else:
                priority = 4
            return priority

        sorted_warehouses = sorted(self.warehouses.values(), key=sort_priority)

        remaining_needed = {item.sku: item.quantity for item in cart_items}
        shipments: List[ShipmentPackage] = []

        # 1. First Pass: Check if a SINGLE warehouse can fulfill the ENTIRE order (no split!)
        for wh in sorted_warehouses:
            can_fulfill_all = all(wh.inventory.get(sku, 0) >= qty for sku, qty in remaining_needed.items())
            if can_fulfill_all:
                zone = "LOCAL" if wh.warehouse_type == "FDC" and wh.region == dest_region else (
                    "REGIONAL" if wh.region == dest_region else "NATIONAL"
                )
                freight = self.ZONE_FREIGHT_MATRIX[zone]
                # Deduct inventory
                for sku, qty in remaining_needed.items():
                    wh.inventory[sku] -= qty

                single_pkg = ShipmentPackage(
                    shipment_id=f"SHP-{uuid.uuid4().hex[:6].upper()}",
                    fulfilling_warehouse_id=wh.warehouse_id,
                    warehouse_name=wh.name,
                    items=dict(remaining_needed),
                    shipping_zone=zone,
                    estimated_freight=freight
                )
                return FulfillmentPlan(
                    order_id=order_id,
                    destination_region=dest_region,
                    total_packages=1,
                    shipments=[single_pkg],
                    is_partially_unfulfilled=False,
                    total_freight_cost=freight
                )

        # 2. Second Pass: Split order across minimum number of priority warehouses
        total_freight = 0.0
        for wh in sorted_warehouses:
            allocated_from_this_wh = {}
            for sku, needed_qty in list(remaining_needed.items()):
                if needed_qty <= 0:
                    continue
                avail = wh.inventory.get(sku, 0)
                if avail > 0:
                    take_qty = min(avail, needed_qty)
                    wh.inventory[sku] -= take_qty
                    remaining_needed[sku] -= take_qty
                    allocated_from_this_wh[sku] = take_qty
                    if remaining_needed[sku] == 0:
                        del remaining_needed[sku]

            if allocated_from_this_wh:
                zone = "LOCAL" if wh.warehouse_type == "FDC" and wh.region == dest_region else (
                    "REGIONAL" if wh.region == dest_region else "NATIONAL"
                )
                freight = self.ZONE_FREIGHT_MATRIX[zone]
                total_freight += freight
                shipments.append(ShipmentPackage(
                    shipment_id=f"SHP-{uuid.uuid4().hex[:6].upper()}",
                    fulfilling_warehouse_id=wh.warehouse_id,
                    warehouse_name=wh.name,
                    items=allocated_from_this_wh,
                    shipping_zone=zone,
                    estimated_freight=freight
                ))

            if not remaining_needed:
                break

        unfulfilled = {k: v for k, v in remaining_needed.items() if v > 0}

        return FulfillmentPlan(
            order_id=order_id,
            destination_region=dest_region,
            total_packages=len(shipments),
            shipments=shipments,
            is_partially_unfulfilled=len(unfulfilled) > 0,
            unfulfilled_items=unfulfilled,
            total_freight_cost=round(total_freight, 2)
        )
