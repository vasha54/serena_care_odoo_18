/** @odoo-module **/
import { Component ,useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");

export class CardInfoResidents extends Component {  // EXPORT
    setup() {
        console.log("CardInfoResidents mounted");
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.state = useState({
            countResidents: 0,
            
        });
        this._loadCardData();
    }

    async _loadCardData() {
        try {
            const result = await this.ormService.call(
                "suite.dashboard",
                "get_count_residents",
                [],
                {}
            );

            this.state.countResidents = result.count_residents;
            console.log("Filter residence data:", result);
        } catch (error) {
            console.error("Error loading filter residence data", error);
        }
    }
}

CardInfoResidents.template = "sc_suite.CardInfoResidentsTemplate";
CardInfoResidents.props = {
    count_residents: { type: Number, optional: true }
};

// También regístralo globalmente
registry.category("components").add("CardInfoResidents", CardInfoResidents);