"""
Mixin utilitaire partagé par tous les modèles interceptés.
Ne pas importer directement — utilisé via héritage dans chaque fichier.
"""


def _fire_webhooks(env, odoo_model, record, action):
    """Déclenche tous les webhooks actifs correspondant au modèle + action."""
    endpoints = env['webhook.endpoint'].sudo().search([
        ('odoo_model', '=', odoo_model),
        ('crud_action', '=', action),
        ('active', '=', True),
    ])
    for endpoint in endpoints:
        try:
            endpoint.fire(record, action)
        except Exception:
            import logging
            logging.getLogger(__name__).exception(
                'Webhook %s failed silently', endpoint.name
            )
