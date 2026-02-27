{
    "name": "Odoo AI Popup Assistant",
    "version": "17.0.1.0.0",
    "summary": "Floating AI Chat Popup for Odoo 17",
    "description": "Enterprise-ready floating AI popup chat integrated with MCP Server",
    "category": "AI",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "odoo_ai_popup/static/src/js/ai_popup.js",
            "odoo_ai_popup/static/src/xml/ai_popup.xml",
            "odoo_ai_popup/static/src/scss/ai_popup.scss",
        ]
    },
    "installable": True,
    "application": False,
}