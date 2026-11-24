# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "fulfillment"
app_title = "Erpnext Multi Warehouse Fulfillment Router"
app_publisher = "Shyamkumar Pandey"
app_description = "Erpnext Multi Warehouse Fulfillment Router - Enterprise Multi-DocType Solution for Frappe & ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/fulfillment/css/fulfillment.bundle.css"
app_include_js = "/assets/fulfillment/js/fulfillment.bundle.js"

# Document Events
# ---------------
doc_events = {
    "Erpnext Multi Warehouse Fulfillment Router Entry": {
        "validate": "fulfillment.services.validator.EnterpriseValidationEngine.validate_compliance_rules",
        "on_submit": "fulfillment.services.integration_service.EnterpriseIntegrationService.verify_remote_status"
    }
}

# Scheduled Background Tasks
# --------------------------
scheduler_events = {
    "hourly": [
        "fulfillment.tasks.hourly_sync"
    ],
    "daily": [
        "fulfillment.tasks.daily_reconciliation"
    ],
    "weekly": [
        "fulfillment.tasks.weekly_digest"
    ]
}
