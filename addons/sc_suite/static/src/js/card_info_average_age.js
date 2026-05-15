/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");

export class CardInfoAverageAge extends Component {  // EXPORT
    setup() {
        console.log("CardInfoAverageAge mounted");
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.state = useState({
            averageAge: 0,
            
        });
        this._loadCardData();
    }

    async _loadCardData() {
        try {
            const result = await this.ormService.call(
                "suite.dashboard",
                "get_age_average",
                [],
                {}
            );

            this.state.averageAge = result.age_average;
            console.log("Filter residence data:", result);
        } catch (error) {
            console.error("Error loading filter residence data", error);
        }
    }
}

CardInfoAverageAge.template = "sc_suite.CardInfoAverageAgeTemplate";
CardInfoAverageAge.props = {
    count_residents: { type: Number, optional: true }
};

// También regístralo globalmente
registry.category("components").add("CardInfoAverageAge", CardInfoAverageAge);