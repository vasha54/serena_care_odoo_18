# -*- coding: utf-8 -*-
{
    'name': "Serena Care - Módulo Núcleo",

    'summary': "Módulo base y núcleo del sistema, contiene funcionalidades esenciales y configuración compartida",

    'description': """
Este módulo constituye la base fundamental del sistema, proporcionando:
        - Modelos base y heredados
        - Configuraciones globales del sistema
        - Utilidades y funciones compartidas
        - Estructuras comunes para todos los módulos
        - Configuración de seguridad base
        
        Todos los módulos del sistema dependen de este núcleo para su correcto funcionamiento.
    """,

    "author": "Serena Care Team",
    "website": "https://www.serena-care.mx",
    "license": "LGPL-3",
    "version": "18.0.1.0.0",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Hidden/Tools",
    

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'web',
        'sc_group',
    ],

    # always loaded
    "data": [
        "data/res_province_mx_data.xml",
        "data/municipality/res_municipality_ags_mx_data.xml",
        "data/municipality/res_municipality_bc_mx_data.xml",
        "data/municipality/res_municipality_bcs_mx_data.xml",
        "data/municipality/res_municipality_camp_mx_data.xml",
        "data/municipality/res_municipality_cdmx_mx_data.xml",
        "data/municipality/res_municipality_chih_mx_data.xml",
        "data/municipality/res_municipality_chis_mx_data.xml",
        "data/municipality/res_municipality_coah_mx_data.xml",
        "data/municipality/res_municipality_col_mx_data.xml",
        "data/municipality/res_municipality_dgo_mx_data.xml",
        "data/municipality/res_municipality_gro_mx_data.xml",
        "data/municipality/res_municipality_gto_mx_data.xml",
        "data/municipality/res_municipality_hgo_mx_data.xml",
        "data/municipality/res_municipality_jal_mx_data.xml",
        "data/municipality/res_municipality_mex_mx_data.xml",
        "data/municipality/res_municipality_mich_mx_data.xml",
        "data/municipality/res_municipality_mor_mx_data.xml",
        "data/municipality/res_municipality_nay_mx_data.xml",
        "data/municipality/res_municipality_nl_mx_data.xml",
        "data/municipality/res_municipality_oax_mx_data.xml",
        "data/municipality/res_municipality_pue_mx_data.xml",
        "data/municipality/res_municipality_qro_mx_data.xml",
        "data/municipality/res_municipality_qroo_mx_data.xml",
        "data/municipality/res_municipality_sin_mx_data.xml",
        "data/municipality/res_municipality_slp_mx_data.xml",
        "data/municipality/res_municipality_son_mx_data.xml",
        "data/municipality/res_municipality_tab_mx_data.xml",
        "data/municipality/res_municipality_tamps_mx_data.xml",
        "data/municipality/res_municipality_tlax_mx_data.xml",
        "data/municipality/res_municipality_ver_mx_data.xml",
        "data/municipality/res_municipality_yuc_mx_data.xml",
        "data/municipality/res_municipality_zac_mx_data.xml",
        "security/ir.model.access.csv",
        "views/res_municipality_mx_views.xml",
        "views/res_province_mx_views.xml",
        "views/wizard/wizard_not_implemented_views.xml",
        "views/view_menu.xml",
    ],
    
    'demo':[], 
    
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
    'post_init_hook': 'post_init_hook',
    'post_update_hook': 'post_update_hook',
}

