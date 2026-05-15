import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount, onPatched, useState, useRef } from "@odoo/owl";
const actionRegistry = registry.category("actions");

export class DoughnutChartHealthStatus extends Component {
    setup() {
        this.canvasRef = useRef("healthStatusDoughnutChart");
        this.chart = null;
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.state = useState({
            loading: true,
            hasData: false,
            labels: [],
            valuesPercent: [],
            values: [],
            colors: [],
        });

        onMounted(() => this._init());
        onPatched(() => this._maybeRenderChart());
        onWillUnmount(() => this._destroyChart());
    }

    // ------------------------------------------------------------
    // Ciclo de vida
    // ------------------------------------------------------------

    async _init() {
        await this._ensureChartJs();
        await this._loadData();
    }

    // ------------------------------------------------------------
    // Data
    // ------------------------------------------------------------

    async _loadData() {
        const result = await this.ormService.call(
            "suite.dashboard",
            "get_health_status",
            [],
            {}
        );

        this.state.labels = result.texts;
        this.state.valuesPercent = result.values_percent;
        this.state.values = result.values;
        this.state.colors = result.colors;
        this.state.hasData = result.has_data;
        this.state.loading = false;
        console.log("Data Doughnut Char healts status:", result);
    }

    // ------------------------------------------------------------
    // Chart.js
    // ------------------------------------------------------------

    async _ensureChartJs() {
        if (window.Chart) {
            return;
        }

        await new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "/sc_suite/static/lib/chart.js/chart.umd.min.js";
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    _maybeRenderChart() {
        if (
            !this.state.loading &&
            this.state.hasData &&
            this.canvasRef.el &&
            !this.chart
        ) {
            this._renderChart();
        }
    }

    _renderChart() {
        if (!this.state.hasData || !this.canvasRef.el) {
            return;
        }

        this._destroyChart();

        const ctx = this.canvasRef.el.getContext("2d");

        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.state.labels,
                datasets: [{
                    data: this.state.values,
                    backgroundColor: this.state.colors,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 15, // Separación al hacer hover
                    cutout: '40%' // Tamaño del agujero central (porcentaje)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true, // Usar puntos en lugar de rectángulos
                            pointStyle: 'circle' // Forma de los puntos
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((context.raw / total) * 100);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    },
                    // Plugin para texto en el centro (opcional)
                    datalabels: {
                        display: false // Requeriría instalar chartjs-plugin-datalabels
                    }
                },
                // Animaciones
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

DoughnutChartHealthStatus.template = "sc_suite.DoughnutChartHealthStatusTemplate";

registry.category("components").add("DoughnutChartHealthStatus", DoughnutChartHealthStatus);