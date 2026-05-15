/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";

const actionRegistry = registry.category("actions");


class ResidenceSelectionDialog extends Dialog {
    static components = { Dialog };

    setup() {
        // ya no necesitamos selectedIds en el state si solo confirmas al final
    }

    confirm() {
        // Construir la lista de seleccionados leyendo los inputs del DOM
        const selected = (this.props.accessibleResidences || [])
            .filter(res => {
                const el = document.getElementById('residence_' + res.id);
                return el && el.checked;
            })
            .map(res => res.id);

        if (this.props.onConfirm) {
            this.props.onConfirm(selected);
        }
        // if (this.props.close) {
        //     this.props.close();
        // }
    }

    onCancel() {
        if (this.props.onCancel) {
            this.props.onCancel();
        }
        if (this.props.close) {
            this.props.close();
        }
    }
}

ResidenceSelectionDialog.template = "sc_suite.ResidenceSelectionDialog";


export class CardFilterResidence extends Component {  // EXPORT
    setup() {
        console.log("CardFilterResidence mounted");
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.dialogService = useService("dialog");


        // Si aún no está disponible
        if (!this.dialogService) {
            console.error("Dialog service is not available in this context");
            // Podrías desactivar la funcionalidad o usar alternativa
        }
        // this.userService = useService("user");

        this.state = useState({
            userId: null,
            selectedCount: 0,
            selectedIds: [],
            accessibleCount: 0,
            accessibleIds: [],
            accessible: [],
            selected: [],
        });
        this._loadCardData();
    }

    async _loadCardData() {
        try {
            const result = await this.ormService.call(
                "suite.dashboard",
                "get_filter_residence",
                [],
                {}
            );

            this.state.userId = result.user_id;
            this.state.selectedCount = result.selected_count;
            this.state.selectedIds = result.selected_ids;
            this.state.accessibleCount = result.accessible_count;
            this.state.accessibleIds = result.accessible_ids;
            this.state.accessible = result.accessible;
            this.state.selected = result.selected;

            console.log("Filter residence data:", result);
        } catch (error) {
            console.error("Error loading filter residence data", error);
        }
    }

    async openFilterResidenceWizard() {
            try {
                // Preparar datos iniciales
                const initialSelectedIds = [...this.state.selectedIds];
                const accessibleResidences = this.state.accessible;
                console.info("Opening filter residence dialog:");
                console.log("Opening wizard...");
                console.log("Dialog service available:", this.dialogService);
                console.log("Accessible residences:", this.state.accessible);
                console.log("Selected IDs:", this.state.selectedIds);

                // Abrir diálogo modal
                this.dialogService.add(ResidenceSelectionDialog, {
                    title: "Seleccionar Residencias",
                    accessibleResidences: this.state.accessible,
                    initialSelectedIds: this.state.selectedIds,
                    onConfirm: async (selectedIds) => {
                        // Actualizar datos locales
                        this.state.selectedIds = selectedIds;
                        this.state.selectedCount = selectedIds.length;
                        console.log("Residencias seleccionadas "+ this.state.selectedIds);

                        // También podrías actualizar la lista 'selected' con objetos completos
                        this.state.selected = accessibleResidences.filter(res =>
                            selectedIds.includes(res.id)
                        );
                        // Cierra el diálogo primero 
                        this.dialogService.closeAll(); 
                        // Ahora sí ejecuta la acción 
                        await this._saveSelection(selectedIds);
                    }
                });

                console.info("Close filter residence dialog:");

            } catch (error) {
                console.error("Error opening filter residence wizard:", error);
            }
        // try {
        //     this.actionService.doAction(
        //         {
        //             type: "ir.actions.act_window",
        //             name: "Filtrar Residencias",
        //             res_model: "res.user.select.residences.wizard",
        //             view_mode: "form",
        //             views: [[false, "form"]],
        //             target: "new",
        //             context: {
        //                 default_user_id: this.state.userId,
        //                 default_selected_residences_ids: [[6, 0, this.state.selectedIds]], 
        //                 default_all_accessible_residences_ids: [[6, 0, this.state.accessibleIds]],
        //             },
        //         },
        //         {
        //             onClose: async () => {
        //                 console.log("Wizard cerrado → refrescando card");
        //                 await this._loadCardData();
        //             },
        //         }
        //     );
        // } catch (error) {
        //     console.error("Error al abrir el wizard:", error);
        // }
    }

    async _saveSelection(selectedIds) {
        try {
            // Aquí llamas al método en el modelo Python para guardar la selección
            const action = await this.ormService.call( 
                "suite.dashboard", 
                "save_residence_selection", [selectedIds], {} 
            ); 
            if (action) { 
                // Ejecutar acción fuera del diálogo 
                await this.actionService.doAction(action); 
            }

            
            
        } catch (error) {
            console.error("Error saving residence selection:", error);
            // Podrías mostrar una notificación de error aquí
            throw error;
        }
    }
}

CardFilterResidence.template = "sc_suite.CardFilterResidenceTemplate";
CardFilterResidence.props = {
    count_residents: { type: Number, optional: true }
};

// También regístralo globalmente
registry.category("components").add("CardFilterResidence", CardFilterResidence);