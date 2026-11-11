# ERPNext Multi-Warehouse Fulfillment Router 🏭📦

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![ERPNext](https://img.shields.io/badge/ERPNext-v14%20%7C%20v15-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

An intelligent multi-warehouse stock allocation, order splitting, and shipping zone freight minimization engine for **ERPNext E-Commerce & Retail Supply Chains** (Amazon FBA / Flipkart multi-fulfillment center model).

---

## 🚀 Key Features

- **Multi-Tier Warehouse Architecture**: Routes orders across Mother Hubs, Regional Distribution Centers (RDC), and Forward Distribution Centers (FDC).
- **Split-Shipment Minimization**: First evaluates whether a single warehouse can ship the complete cart to reduce packaging and courier costs.
- **Zone Freight Optimization**: Distinguishes between Local, Regional, and National transport costs to reduce carbon footprint and shipping bills.
- **Direct ERPNext Stock Reservation**: Generates ERPNext `Delivery Note` & `Stock Entry` documents for each allocated warehouse package.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/shyampandey1104/erpnext-multi-warehouse-fulfillment-router.git
cd erpnext-multi-warehouse-fulfillment-router
pip install -r requirements.txt
```

---

## 🛠️ Usage Example

```python
from fulfillment.engine import MultiWarehouseFulfillmentRouter, Warehouse, CartItem

router = MultiWarehouseFulfillmentRouter()

router.register_warehouse(Warehouse(
    warehouse_id="WH-DELHI",
    name="North Regional Hub",
    warehouse_type="RDC",
    region="NORTH",
    inventory={"SMARTPHONE-X": 15}
))

plan = router.route_order(
    order_id="ORD-901",
    dest_region="NORTH",
    cart_items=[CartItem(sku="SMARTPHONE-X", quantity=2, unit_price=45000.0)]
)

print(f"Total Packages: {plan.total_packages} | Warehouse: {plan.shipments[0].warehouse_name} | Freight: ₹{plan.total_freight_cost}")
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License
MIT License. Created with ❤️ by [Shyam Pandey](https://github.com/shyampandey1104).
