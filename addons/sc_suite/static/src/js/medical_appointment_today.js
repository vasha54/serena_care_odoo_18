import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount, onPatched, useState, useRef } from "@odoo/owl";
const actionRegistry = registry.category("actions");

export class MedicalAppointmentToday extends Component {
    setup() {
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.state = useState({
            loading: true,
            hasData: false,
            appointments: [],
        });
        
        onMounted(() => this._init());
    }
    
    // ------------------------------------------------------------
    // Ciclo de vida
    // ------------------------------------------------------------

    async _init() {
        await this._loadData();
    }

    // ------------------------------------------------------------
    // Data
    // ------------------------------------------------------------

    async _loadData() {
        const result = await this.ormService.call(
            "suite.dashboard",
            "get_appointment_today",
            [],
            {}
        );

        this.state.appointments = result.appointments;
        this.state.hasData = result.has_data;
        this.state.loading = false;
        console.log("Medical Appointment Today:", result);
    }
    
}

MedicalAppointmentToday.template = "sc_suite.MedicalAppointmentTodayTemplate";
registry.category("components").add("MedicalAppointmentToday", MedicalAppointmentToday);