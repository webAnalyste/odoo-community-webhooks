{
    'name': 'Customisations affichage',
    'version': '18.0.1.0.0',
    'summary': 'Personnalisations des templates PDF et des vues portail client',
    'description': """
Fonctions incluses :

PDF Devis
---------
- Affiche la date de livraison promise (commitment_date) dans l'en-tête du devis

PDF Facture
-----------
- Pour les factures liées à une opportunité CRM de l'équipe Formations, affiche en bas de facture :
  - Liste des stagiaires
  - Période de formation (date début → date fin)
  - Nombre d'heures

Portail client
--------------
- Placeholder pour futures customisations (rien d'actif pour l'instant)
""",
    'author': 'Franck Scandolera',
    'category': 'Technical',
    'license': 'LGPL-3',
    'depends': ['account', 'sale', 'crm'],
    'data': [
        'templates/sale_order_templates.xml',
        'templates/invoice_templates.xml',
        'templates/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
}
