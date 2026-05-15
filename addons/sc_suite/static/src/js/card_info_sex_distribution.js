/** @odoo-module **/
import { Component ,useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");

export class CardInfoSexDistribution extends Component {  // EXPORT
    setup() {
        console.log("CardInfoSexDistribution mounted");
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.state = useState({
            residentsFemale: 0,
            residentsMale: 0,
        });
        this._loadCardData();
    }

    async _loadCardData() {
        try {
            const result = await this.ormService.call(
                "suite.dashboard",
                "get_sex_distribution",
                [],
                {}
            );

            this.state.residentsMale = result.residents_male;
            this.state.residentsFemale = result.residents_female;
            console.log("Filter residence data:", result);
        } catch (error) {
            console.error("Error loading filter residence data", error);
        }
    }
}

CardInfoSexDistribution.template = "sc_suite.CardInfoSexDistributionTemplate";
CardInfoSexDistribution.props = {
    count_residents: { type: Number, optional: true }
};

// También regístralo globalmente
registry.category("components").add("CardInfoSexDistribution", CardInfoSexDistribution);