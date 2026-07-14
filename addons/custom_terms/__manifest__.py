{
    'name': 'Conditions générales par type de document',
    'version': '18.0.1.0.0',
    'summary': 'Ajoute des CG spécifiques pour les Devis et les Factures',
    'author': 'Franck Scandolera',
    'category': 'Technical',
    'license': 'LGPL-3',
    'depends': ['account', 'sale'],
    'data': [
        'views/res_config_settings_views.xml',
        'report/sale_order_terms.xml',
        'report/invoice_terms.xml',
    ],
    'installable': True,
    'application': False,
}
