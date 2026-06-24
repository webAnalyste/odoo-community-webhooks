{
    'name': 'Webhook Connector',
    'version': '18.0.1.0.0',
    'summary': 'Déclenche des webhooks externes sur les actions CRUD des objets métier Odoo',
    'author': 'Custom',
    'category': 'Technical',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'sale', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/webhook_endpoint_views.xml',
        'views/webhook_log_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}
