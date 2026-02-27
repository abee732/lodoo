/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class AIPopup extends Component {
    setup() {
        this.state = useState({
            open: false,
            input: "",
            messages: [],
            loading: false,
        });
        this.rpc = useService("rpc");
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    async send() {
        if (!this.state.input.trim()) return;

        const userMsg = this.state.input;
        this.state.messages.push({ role: "user", content: userMsg });
        this.state.input = "";
        this.state.loading = true;

        try {
            const res = await this.rpc("/ai/chat", {
                message: userMsg,
            });

            this.state.messages.push({
                role: "assistant",
                content: res.reply || "No response",
            });

        } catch (err) {
            this.state.messages.push({
                role: "assistant",
                content: "⚠️ Không thể kết nối AI Server",
            });
        } finally {
            this.state.loading = false;
        }
    }
}

AIPopup.template = "odoo_ai_popup.AIPopup";

registry.category("main_components").add("AIPopup", {
    Component: AIPopup,
});