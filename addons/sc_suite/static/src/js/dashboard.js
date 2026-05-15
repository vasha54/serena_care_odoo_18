/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount, useState, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import {CardInfoResidents} from "./card_info_residents.js";
import {CardInfoAverageAge} from "./card_info_average_age.js";
import {CardInfoTimeResidence} from "./card_info_time_residence.js";
import {CardInfoSexDistribution} from "./card_info_sex_distribution.js";
import {CardFilterResidence} from "./card_filter_residence.js";
import {PieChartDistributionAge} from "./pie_chart_distribution_age.js";
import {BarChartWeekAppointments} from "./bar_chart_week_appointments.js";
import {DoughnutChartHealthStatus} from "./doughnut_chart_health_status.js";
import {MedicalAppointmentToday} from "./medical_appointment_today.js";
const actionRegistry = registry.category("actions");


class SerenaCareDashboard extends Component {
    static components = { 
        CardInfoResidents,
        CardInfoAverageAge,
        CardInfoTimeResidence,
        CardInfoSexDistribution,
        CardFilterResidence,
        MedicalAppointmentToday,
        PieChartDistributionAge, 
        BarChartWeekAppointments,
        DoughnutChartHealthStatus ,
     };
    
    setup() {
        // Definir los datos que queremos pasar al gráfico
        // Estos datos podrían venir de una llamada RPC en un caso real
        this.chartData = {
            labels: [
                'Menos de 60 años',
                '60 - 69 años',
                '70 - 79 años',
                '80 - 89 años',
                '90 - 99 años',
                'Más de 100 años'
            ],
            data: [15, 25, 20, 18, 12, 10], // Ejemplo de datos diferentes
            colors: [
                '#92b8ee',
                '#6e67b5',
                '#88bc6a',
                '#f7b239',
                '#f05261',
                '#56aaf2'
            ]
        };

        // Datos para el gráfico de estado de salud
        this.healthStatusData = {
            labels: ['Desconocido', 'Crítico', 'En Observación', 'Estable'],
            data: [18, 25, 112, 175], // Valores de ejemplo
            colors: ['#95a5a6', '#e74c3c', '#f39c12', '#27ae60'],
            title: 'Estado de Salud de Residentes'
        };
        this.actionService = useService("action");
        this.orm = useService("orm");
        
        console.log('Dashboard inicializado. User service:', this.userService);
    }

}

SerenaCareDashboard.template = "sc_suite.SerenaCareDashboard";
// Register the component with the action tag
actionRegistry.add("serena_care_dashboard_tag", SerenaCareDashboard);