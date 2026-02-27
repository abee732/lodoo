from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)

MCP_URL = "https://mcp.bms360.cloud/chat"

class AIAssistantController(http.Controller):

    @http.route('/ai/chat', type='json', auth='user', csrf=False)
    def ai_chat(self, message):
        try:
            res = requests.post(
                MCP_URL,
                json={"message": message},
                timeout=60
            )
            res.raise_for_status()
            return res.json()

        except Exception as e:
            _logger.exception("AI connection error")
            return {"reply": f"⚠️ AI Server Error: {str(e)}"}