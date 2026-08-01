/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";

export class WhatsappPosPopup extends Component {
    static template = "eco_whatsapp_integration.WhatsappPosPopup";
    static components = { Dialog };
    static props = {
        close: Function,
        phone: { type: String, optional: true },
        orderId: { type: Number, optional: true },
        printReceipt: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            phone: this.props.phone || "",
            error: "",
            loading: false,
        });
    }

    async sendWhatsApp() {
        const rawPhone = this.state.phone;
        const cleanedPhone = rawPhone.replace(/[^\d+]/g, '');
        if (!cleanedPhone) {
            this.state.error = _t("Please enter a valid phone number.");
            return;
        }

        this.state.loading = true;
        this.state.error = "";

        try {
            const result = await this.orm.call(
                "pos.order",
                "action_get_pos_whatsapp_url",
                [this.props.orderId, cleanedPhone]
            );
            if (result && result.url) {
                window.open(result.url, "_blank");
                this.props.close();
            } else {
                this.state.error = _t("Could not generate WhatsApp URL.");
            }
        } catch (err) {
            this.state.error = _t("Server error: ") + (err.message || _t("Unknown error"));
        } finally {
            this.state.loading = false;
        }
    }

    printReceipt() {
        this.props.printReceipt();
        this.props.close();
    }
}

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
        
        onMounted(() => {
            const order = this.pos.get_order();
            if (order) {
                // Get customer phone if set
                const partner = order.get_partner();
                const phone = partner ? (partner.mobile || partner.phone || "") : "";
                
                // Server ID is set on order after sync
                const orderId = order.server_id || order.id;

                this.dialogService.add(WhatsappPosPopup, {
                    phone: phone,
                    orderId: orderId,
                    printReceipt: () => {
                        if (typeof this.printReceipt === "function") {
                            this.printReceipt();
                        } else if (this.pos && typeof this.pos.printReceipt === "function") {
                            this.pos.printReceipt();
                        }
                    },
                });
            }
        });
    }
});
