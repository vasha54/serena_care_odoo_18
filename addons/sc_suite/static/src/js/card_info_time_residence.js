/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");

export class CardInfoTimeResidence extends Component {  // EXPORT
    setup() {
        console.log("CardInfoTimeResidence mounted");
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.state = useState({
            value: 0,
            unit: 'días',
            
        });
        this._loadCardData();
    }

    async _loadCardData() {
        try {
            const result = await this.ormService.call(
                "suite.dashboard",
                "get_time_average_residence",
                [],
                {}
            );

            this.state.value = result.value;
            this.state.unit = result.unit;
            console.log("CardInfoTimeResidence data:", result);
        } catch (error) {
            console.error("Error loading filter residence data", error);
        }
    }
}

CardInfoTimeResidence.template = "sc_suite.CardInfoTimeResidenceTemplate";
CardInfoTimeResidence.props = {
    count_residents: { type: Number, optional: true }
};

// También regístralo globalmente
registry.category("components").add("CardInfoTimeResidence", CardInfoTimeResidence);