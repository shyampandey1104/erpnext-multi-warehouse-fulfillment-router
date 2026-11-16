# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "fulfillment"
app_title = "Erpnext Multi Warehouse Fulfillment Router"
app_publisher = "Shyamkumar Pandey"
app_description = "Erpnext Multi Warehouse Fulfillment Router for Frappe and ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/fulfillment/css/fulfillment.bundle.css"
app_include_js = "/assets/fulfillment/js/fulfillment.bundle.js"

# Document Events
# ---------------
doc_events = {
    "DocType Event": {
        "on_submit": "fulfillment.engine.on_document_submit",
        "on_cancel": "fulfillment.engine.on_document_cancel"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "fulfillment.engine.daily_scheduled_sync"
    ]
}
