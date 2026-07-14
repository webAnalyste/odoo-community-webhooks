from odoo import http
from odoo.http import Response


class RestApiDocController(http.Controller):

    @http.route('/api/v1/doc', type='http', auth='user', methods=['GET'], csrf=False)
    def doc(self, **kwargs):
        html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>REST API Connector \u2014 Documentation</title>
<style>
* { box-sizing: border-box; }
body { font-family: sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 20px; color: #333; }
h1 { color: #7c7bad; }
h2 { color: #7c7bad; border-bottom: 2px solid #7c7bad; padding-bottom: 6px; margin-top: 36px; }
h3 { color: #555; margin-top: 20px; margin-bottom: 8px; }
label { font-weight: bold; display: block; margin-bottom: 4px; }
.btn-copy { background: #5a5a8a; color: white; font-size: 12px; position: absolute; top: 8px; right: 8px; padding: 4px 10px; border-radius: 3px; cursor: pointer; border: none; }
pre { background: #1e1e2e; color: #cdd6f4; padding: 16px 16px 16px 16px; border-radius: 6px; font-size: 12.5px; line-height: 1.6; white-space: pre-wrap; word-break: break-all; position: relative; margin: 0; }
.pre-wrap { position: relative; margin-bottom: 10px; }
details { margin-bottom: 12px; }
summary { cursor: pointer; font-weight: bold; padding: 8px 12px; background: #f4f4f4; border-radius: 4px; }
summary:hover { background: #eaeaf4; }
table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 8px; }
th { background: #7c7bad; color: white; padding: 8px; text-align: left; }
td { padding: 8px; border-bottom: 1px solid #eee; vertical-align: top; }
code { background: #f0f0f8; padding: 2px 5px; border-radius: 3px; font-size: 12.5px; font-family: monospace; }
.badge { display: inline-block; padding: 2px 7px; border-radius: 3px; font-size: 11px; font-weight: bold; color: white; margin-right: 4px; }
.get { background: #2196f3; }
.post { background: #4caf50; }
.put { background: #ff9800; }
.del { background: #f44336; }
.warn { background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; padding: 10px 14px; margin-bottom: 16px; }
.info { background: #e3f2fd; border: 1px solid #90caf9; border-radius: 4px; padding: 10px 14px; margin-bottom: 16px; }
.endpoint-grid { display: grid; grid-template-columns: auto 1fr; gap: 6px 12px; align-items: start; margin-bottom: 16px; }
.ep-method { font-family: monospace; }
.ep-url { font-family: monospace; color: #7c7bad; }
.ep-desc { color: #666; font-size: 13px; }
</style>
</head>
<body>
<h1>REST API Connector \u2014 Documentation</h1>
<div class="info">
  <strong>Authentification :</strong> toutes les requ\u00eates n\u00e9cessitent le header <code>X-API-Key: &lt;votre_cl\u00e9&gt;</code><br>
  <strong>Base URL :</strong> <code>https://odoo.webanalyste.com</code> &nbsp;&bull;&nbsp;
  <strong>Content-Type (POST/PUT) :</strong> <code>application/json</code>
</div>


<h2>Endpoints</h2>
<details open>
  <summary>Entreprises \u2014 <code>/api/v1/companies</code></summary>
  <div style="padding:12px 8px;">
  <div class="endpoint-grid">
    <span class="ep-method"><span class="badge get">GET</span></span><span class="ep-url">/api/v1/companies</span>
    <span></span><span class="ep-desc">Liste et filtre les entreprises. R\u00e9ponse : <code>{total, limit, offset, results[]}</code></span>
    <span class="ep-method"><span class="badge get">GET</span></span><span class="ep-url">/api/v1/companies/{id}</span>
    <span></span><span class="ep-desc">D\u00e9tail d\u2019une entreprise</span>
    <span class="ep-method"><span class="badge post">POST</span></span><span class="ep-url">/api/v1/companies</span>
    <span></span><span class="ep-desc">Cr\u00e9er une entreprise. <code>name</code> obligatoire. R\u00e9ponse HTTP 201.</span>
    <span class="ep-method"><span class="badge put">PUT</span></span><span class="ep-url">/api/v1/companies/{id}</span>
    <span></span><span class="ep-desc">Modifier une entreprise (champs partiels accept\u00e9s)</span>
    <span class="ep-method"><span class="badge del">DELETE</span></span><span class="ep-url">/api/v1/companies/{id}</span>
    <span></span><span class="ep-desc">Archiver une entreprise (r\u00e9versible, <code>active=false</code>)</span>
  </div>
  <table><thead><tr><th>Champ</th><th>Type</th><th>Lecture</th><th>Ecriture</th><th>Notes</th></tr></thead><tbody>
    <tr><td><code>id</code></td><td>entier</td><td>oui</td><td>non</td><td>Identifiant Odoo</td></tr>
    <tr><td><code>name</code></td><td>texte</td><td>oui</td><td>oui</td><td><strong>Obligatoire \u00e0 la cr\u00e9ation</strong></td></tr>
    <tr><td><code>email</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>phone</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>mobile</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>website</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>vat</code></td><td>texte</td><td>oui</td><td>oui</td><td>N\u00b0 TVA intracommunautaire</td></tr>
    <tr><td><code>siret</code></td><td>texte</td><td>oui</td><td>oui</td><td>SIRET (module l10n_fr_siret)</td></tr>
    <tr><td><code>street</code></td><td>texte</td><td>oui</td><td>oui</td><td>Adresse ligne 1</td></tr>
    <tr><td><code>street2</code></td><td>texte</td><td>oui</td><td>oui</td><td>Adresse ligne 2</td></tr>
    <tr><td><code>city</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>zip</code></td><td>texte</td><td>oui</td><td>oui</td><td>Code postal</td></tr>
    <tr><td><code>country_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>75 = France. R\u00e9ponse inclut aussi <code>country_name</code></td></tr>
    <tr><td><code>state_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>D\u00e9partement/r\u00e9gion. R\u00e9ponse inclut aussi <code>state_name</code></td></tr>
    <tr><td><code>lang</code></td><td>texte</td><td>oui</td><td>oui</td><td>ex: <code>fr_FR</code>, <code>en_US</code></td></tr>
    <tr><td><code>active</code></td><td>bool\u00e9en</td><td>oui</td><td>oui</td><td><code>true</code> / <code>false</code></td></tr>
    <tr><td><code>contact_count</code></td><td>entier</td><td>oui</td><td>non</td><td>Nombre de contacts rattach\u00e9s</td></tr>
  </tbody></table>
  </div>
</details>

<details>
  <summary>Contacts \u2014 <code>/api/v1/contacts</code></summary>
  <div style="padding:12px 8px;">
  <div class="endpoint-grid">
    <span class="ep-method"><span class="badge get">GET</span></span><span class="ep-url">/api/v1/contacts</span>
    <span></span><span class="ep-desc">Liste et filtre les contacts (personnes physiques). R\u00e9ponse : <code>{total, limit, offset, results[]}</code></span>
    <span class="ep-method"><span class="badge get">GET</span></span><span class="ep-url">/api/v1/contacts/{id}</span>
    <span></span><span class="ep-desc">D\u00e9tail d\u2019un contact</span>
    <span class="ep-method"><span class="badge post">POST</span></span><span class="ep-url">/api/v1/contacts</span>
    <span></span><span class="ep-desc">Cr\u00e9er un contact. <code>name</code> obligatoire. R\u00e9ponse HTTP 201.</span>
    <span class="ep-method"><span class="badge put">PUT</span></span><span class="ep-url">/api/v1/contacts/{id}</span>
    <span></span><span class="ep-desc">Modifier un contact (champs partiels accept\u00e9s)</span>
    <span class="ep-method"><span class="badge del">DELETE</span></span><span class="ep-url">/api/v1/contacts/{id}</span>
    <span></span><span class="ep-desc">Archiver un contact (<code>active=false</code>)</span>
  </div>
  <table><thead><tr><th>Champ</th><th>Type</th><th>Lecture</th><th>Ecriture</th><th>Notes</th></tr></thead><tbody>
    <tr><td><code>id</code></td><td>entier</td><td>oui</td><td>non</td><td></td></tr>
    <tr><td><code>name</code></td><td>texte</td><td>oui</td><td>oui</td><td><strong>Obligatoire \u00e0 la cr\u00e9ation</strong></td></tr>
    <tr><td><code>email</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>phone</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>mobile</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>function</code></td><td>texte</td><td>oui</td><td>oui</td><td>Poste / fonction</td></tr>
    <tr><td><code>parent_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>ID de l\u2019entreprise li\u00e9e. R\u00e9ponse inclut aussi <code>parent_name</code></td></tr>
    <tr><td><code>type</code></td><td>texte</td><td>oui</td><td>oui</td><td><code>contact</code>, <code>invoice</code>, <code>delivery</code>, <code>other</code></td></tr>
    <tr><td><code>street</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>street2</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>city</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>zip</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>country_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>75 = France. R\u00e9ponse inclut aussi <code>country_name</code></td></tr>
    <tr><td><code>state_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>R\u00e9ponse inclut aussi <code>state_name</code></td></tr>
    <tr><td><code>comment</code></td><td>texte</td><td>oui</td><td>oui</td><td>Notes internes</td></tr>
    <tr><td><code>active</code></td><td>bool\u00e9en</td><td>oui</td><td>oui</td><td><code>true</code> / <code>false</code></td></tr>
  </tbody></table>
  </div>
</details>

<details>
  <summary>Opportunit\u00e9s CRM \u2014 <code>/api/v1/crm/leads</code></summary>
  <div style="padding:12px 8px;">
  <div class="endpoint-grid">
    <span class="ep-method"><span class="badge get">GET</span></span><span class="ep-url">/api/v1/crm/leads</span>
    <span></span><span class="ep-desc">Liste et filtre les opportunit\u00e9s (tri par date cr\u00e9ation desc). R\u00e9ponse : <code>{total, limit, offset, results[]}</code></span>
    <span class="ep-method"><span class="badge get">GET</span></span><span class="ep-url">/api/v1/crm/leads/{id}</span>
    <span></span><span class="ep-desc">D\u00e9tail d\u2019une opportunit\u00e9</span>
    <span class="ep-method"><span class="badge post">POST</span></span><span class="ep-url">/api/v1/crm/leads</span>
    <span></span><span class="ep-desc">Cr\u00e9er une opportunit\u00e9. <code>name</code> obligatoire. R\u00e9ponse HTTP 201.</span>
    <span class="ep-method"><span class="badge put">PUT</span></span><span class="ep-url">/api/v1/crm/leads/{id}</span>
    <span></span><span class="ep-desc">Modifier une opportunit\u00e9 (champs partiels accept\u00e9s)</span>
    <span class="ep-method"><span class="badge del">DELETE</span></span><span class="ep-url">/api/v1/crm/leads/{id}</span>
    <span></span><span class="ep-desc">Archiver une opportunit\u00e9 (<code>active=false</code>)</span>
  </div>
  <table><thead><tr><th>Champ</th><th>Type</th><th>Lecture</th><th>Ecriture</th><th>Notes</th></tr></thead><tbody>
    <tr><td><code>id</code></td><td>entier</td><td>oui</td><td>non</td><td></td></tr>
    <tr><td><code>name</code></td><td>texte</td><td>oui</td><td>oui</td><td><strong>Titre \u2014 obligatoire \u00e0 la cr\u00e9ation</strong></td></tr>
    <tr><td><code>partner_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>ID entreprise/contact li\u00e9. R\u00e9ponse inclut aussi <code>partner_name</code></td></tr>
    <tr><td><code>email_from</code></td><td>texte</td><td>oui</td><td>oui</td><td>Email du prospect</td></tr>
    <tr><td><code>phone</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>mobile</code></td><td>texte</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>stage_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>\u00c9tape pipeline. R\u00e9ponse inclut aussi <code>stage_name</code></td></tr>
    <tr><td><code>user_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>Commercial assign\u00e9. R\u00e9ponse inclut aussi <code>user_name</code></td></tr>
    <tr><td><code>team_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>\u00c9quipe commerciale. R\u00e9ponse inclut aussi <code>team_name</code></td></tr>
    <tr><td><code>priority</code></td><td>texte</td><td>oui</td><td>oui</td><td><code>0</code> normal, <code>1</code> basse, <code>2</code> haute, <code>3</code> tr\u00e8s haute</td></tr>
    <tr><td><code>probability</code></td><td>d\u00e9cimal</td><td>oui</td><td>oui</td><td>0 \u00e0 100</td></tr>
    <tr><td><code>expected_revenue</code></td><td>d\u00e9cimal</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>description</code></td><td>texte</td><td>oui</td><td>oui</td><td>Notes internes</td></tr>
    <tr><td><code>date_deadline</code></td><td>date</td><td>oui</td><td>oui</td><td>Format <code>YYYY-MM-DD</code></td></tr>
    <tr><td><code>tag_ids</code></td><td>liste d\u2019entiers</td><td>oui</td><td>oui</td><td>ex: <code>[1, 2, 3]</code>. R\u00e9ponse inclut aussi <code>tag_names</code></td></tr>
    <tr><td><code>create_date</code></td><td>datetime</td><td>oui</td><td>non</td><td>Date de cr\u00e9ation</td></tr>
    <tr><td><code>write_date</code></td><td>datetime</td><td>oui</td><td>non</td><td>Derni\u00e8re modification</td></tr>
    <tr><td><code>active</code></td><td>bool\u00e9en</td><td>oui</td><td>oui</td><td></td></tr>
    <tr><td><code>x_participants</code></td><td>entier</td><td>oui</td><td>oui</td><td>Nombre de stagiaires</td></tr>
    <tr><td><code>x_date_debut</code></td><td>date</td><td>oui</td><td>oui</td><td>Format <code>YYYY-MM-DD</code></td></tr>
    <tr><td><code>x_date_fin</code></td><td>date</td><td>oui</td><td>oui</td><td>Format <code>YYYY-MM-DD</code></td></tr>
    <tr><td><code>x_nb_heures</code></td><td>d\u00e9cimal</td><td>oui</td><td>oui</td><td>Dur\u00e9e de la formation</td></tr>
    <tr><td><code>x_contact_id</code></td><td>entier (ID)</td><td>oui</td><td>oui</td><td>Contact client li\u00e9. R\u00e9ponse inclut aussi <code>x_contact_name</code>, <code>x_contact_email</code></td></tr>
    <tr><td><code>x_stagiaires</code></td><td>texte</td><td>oui</td><td>oui</td><td>Noms des stagiaires</td></tr>
    <tr><td><code>x_stagiaires_emails</code></td><td>texte</td><td>oui</td><td>oui</td><td>Emails des stagiaires</td></tr>
  </tbody></table>
  <h3>Filtres sp\u00e9ciaux (CRM uniquement)</h3>
  <table><thead><tr><th>Param\u00e8tre</th><th>Description</th><th>Exemple</th></tr></thead><tbody>
    <tr><td><code>created_after=YYYY-MM-DD</code></td><td>Cr\u00e9\u00e9 apr\u00e8s cette date</td><td><code>created_after=2026-01-01</code></td></tr>
    <tr><td><code>created_before=YYYY-MM-DD</code></td><td>Cr\u00e9\u00e9 avant cette date</td><td><code>created_before=2026-12-31</code></td></tr>
    <tr><td><code>updated_after=YYYY-MM-DD</code></td><td>Modifi\u00e9 apr\u00e8s cette date</td><td><code>updated_after=2026-07-01</code></td></tr>
  </tbody></table>
  </div>
</details>

<h2>Filtres g\u00e9n\u00e9raux (GET liste)</h2>
<table>
  <thead><tr><th>Syntaxe</th><th>Op\u00e9rateur</th><th>Exemple</th></tr></thead>
  <tbody>
    <tr><td><code>champ=valeur</code></td><td>\u00c9galit\u00e9 exacte</td><td><code>city=Paris</code> &nbsp; <code>stage_id=3</code> &nbsp; <code>active=false</code></td></tr>
    <tr><td><code>champ__like=valeur</code></td><td>Contient (insensible casse)</td><td><code>name__like=veolia</code> &nbsp; <code>partner_name__like=total</code></td></tr>
    <tr><td><code>champ__gte=valeur</code></td><td>&ge; sup\u00e9rieur ou \u00e9gal</td><td><code>expected_revenue__gte=1000</code></td></tr>
    <tr><td><code>champ__lte=valeur</code></td><td>&le; inf\u00e9rieur ou \u00e9gal</td><td><code>expected_revenue__lte=5000</code></td></tr>
    <tr><td><code>limit=N</code></td><td>Nombre de r\u00e9sultats (max 500)</td><td><code>limit=50</code> &mdash; d\u00e9faut 100</td></tr>
    <tr><td><code>offset=N</code></td><td>Pagination</td><td><code>offset=100</code></td></tr>
  </tbody>
</table>

<h2>Exemples curl</h2>

<h3>Lister les entreprises \u00e0 Paris</h3>
<div class="pre-wrap">
<pre>curl -s -H "X-API-Key: VOTRE_CLE" \\
  "https://odoo.webanalyste.com/api/v1/companies?city=Paris&limit=20"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>D\u00e9tail d\u2019une entreprise (id=42)</h3>
<div class="pre-wrap">
<pre>curl -s -H "X-API-Key: VOTRE_CLE" \\
  "https://odoo.webanalyste.com/api/v1/companies/42"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Cr\u00e9er une entreprise</h3>
<div class="pre-wrap">
<pre>curl -s -X POST \\
  -H "X-API-Key: VOTRE_CLE" \\
  -H "Content-Type: application/json" \\
  -d '{"name": "Acme SA", "email": "contact@acme.fr", "phone": "0600000000", "city": "Paris", "zip": "75001", "country_id": 75, "vat": "FR12345678901"}' \\
  "https://odoo.webanalyste.com/api/v1/companies"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Modifier une entreprise (id=42)</h3>
<div class="pre-wrap">
<pre>curl -s -X PUT \\
  -H "X-API-Key: VOTRE_CLE" \\
  -H "Content-Type: application/json" \\
  -d '{"phone": "0600000001", "website": "https://acme.fr"}' \\
  "https://odoo.webanalyste.com/api/v1/companies/42"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Archiver une entreprise (id=42)</h3>
<div class="pre-wrap">
<pre>curl -s -X DELETE \\
  -H "X-API-Key: VOTRE_CLE" \\
  "https://odoo.webanalyste.com/api/v1/companies/42"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Cr\u00e9er un contact rattach\u00e9 \u00e0 une entreprise</h3>
<div class="pre-wrap">
<pre>curl -s -X POST \\
  -H "X-API-Key: VOTRE_CLE" \\
  -H "Content-Type: application/json" \\
  -d '{"name": "Marie Dupont", "function": "DRH", "email": "m.dupont@acme.fr", "mobile": "0612345678", "parent_id": 42}' \\
  "https://odoo.webanalyste.com/api/v1/contacts"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Chercher les contacts d\u2019une entreprise</h3>
<div class="pre-wrap">
<pre>curl -s -H "X-API-Key: VOTRE_CLE" \\
  "https://odoo.webanalyste.com/api/v1/contacts?parent_id=42"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Lister les opportunit\u00e9s cr\u00e9\u00e9es apr\u00e8s le 1er janvier 2026</h3>
<div class="pre-wrap">
<pre>curl -s -H "X-API-Key: VOTRE_CLE" \\
  "https://odoo.webanalyste.com/api/v1/crm/leads?created_after=2026-01-01&limit=50"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Cr\u00e9er une opportunit\u00e9 CRM avec champs custom formation</h3>
<div class="pre-wrap">
<pre>curl -s -X POST \\
  -H "X-API-Key: VOTRE_CLE" \\
  -H "Content-Type: application/json" \\
  -d '{"name": "Formation Python - Acme SA", "partner_id": 42, "stage_id": 1, "expected_revenue": 2500.00, "x_participants": 8, "x_date_debut": "2026-09-01", "x_date_fin": "2026-09-05", "x_nb_heures": 35}' \\
  "https://odoo.webanalyste.com/api/v1/crm/leads"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<h3>Modifier le stage d\u2019une opportunit\u00e9 (id=99)</h3>
<div class="pre-wrap">
<pre>curl -s -X PUT \\
  -H "X-API-Key: VOTRE_CLE" \\
  -H "Content-Type: application/json" \\
  -d '{"stage_id": 3, "probability": 75}' \\
  "https://odoo.webanalyste.com/api/v1/crm/leads/99"</pre>
<button class="btn-copy" onclick="copyPre(this)">Copier</button>
</div>

<script>
function copyPre(btn) {
  var pre = btn.parentElement.querySelector('pre');
  navigator.clipboard.writeText(pre.textContent).then(function() {
    var orig = btn.textContent; btn.textContent = 'Copie !';
    setTimeout(function(){ btn.textContent = orig; }, 2000);
  });
}
</script>
</body></html>"""
        return Response(html, content_type='text/html;charset=utf-8')
