import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount, onPatched, useState, useRef } from "@odoo/owl";
const actionRegistry = registry.category("actions");

export class PieChartDistributionAge extends Component {
    setup() {
        this.canvasRef = useRef("agePieChart");
        this.chart = null;
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.state = useState({
            loading: true,
            hasData: false,
            labels: [],
            valuesPercent: [],
            values: [],
            legends: [],
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
            "get_distribution_age",
            [],
            {}
        );

        this.state.labels = result.texts;
        this.state.valuesPercent = result.values_percent;
        this.state.values = result.values;
        this.state.colors = result.colors;
        this.state.hasData = result.has_data;
        this.state.legends = result.legends
        this.state.loading = false;
        console.log("Data Pie Char distribution age:", result);
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
            type: "pie",
            data: {
                labels: this.state.labels,
                datasets: [{
                    data: this.state.valuesPercent,
                    backgroundColor: this.state.colors,
                    borderWidth: 1,
                    borderColor: "#fff",
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) =>
                                `${context.label}: ${context.parsed}%`,
                        },
                    },
                },
            },
        });
    }

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

PieChartDistributionAge.template = "sc_suite.PieChartDistributionAgeTemplate";

registry.category("components").add("PieChartDistributionAge", PieChartDistributionAge);