from odoo import http
from odoo.http import request, Response


class RestApiDocController(http.Controller):

    @http.route('/api/v1/doc', type='http', auth='user', methods=['GET'], csrf=False)
    def doc(self, **kwargs):
        html = u"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>REST API Connector \u2014 G\xe9n\xe9rateur</title>
<style>
* { box-sizing: border-box; }
body { font-family: sans-serif; max-width: 1000px; margin: 40px auto; padding: 0 20px; color: #333; }
h1 { color: #7c7bad; }
h2 { color: #7c7bad; border-bottom: 2px solid #7c7bad; padding-bottom: 6px; margin-top: 30px; }
label { font-weight: bold; display: block; margin-bottom: 4px; }
select, input[type=text], input[type=number], textarea { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
.row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
.row > div { flex: 1; min-width: 200px; }
.filter-row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.filter-row input { flex: 2; }
.filter-row select { flex: 1; }
button { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.btn-add { background: #7c7bad; color: white; margin-bottom: 12px; }
.btn-remove { background: #e55; color: white; padding: 8px 12px; flex-shrink: 0; }
.btn-preset { background: #eee; border: 1px solid #ccc; margin-top: 6px; font-size: 13px; display:none; }
.btn-copy { background: #7c7bad; color: white; font-size: 12px; position: absolute; top: 8px; right: 8px; }
pre { background: #1e1e2e; color: #cdd6f4; padding: 16px; border-radius: 6px; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-break: break-all; position: relative; margin: 0; }
.pre-wrap { position: relative; }
.box { background: #f9f9fc; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 30px; }
details { margin-bottom: 12px; }
summary { cursor: pointer; font-weight: bold; padding: 8px; background: #f4f4f4; border-radius: 4px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 8px; }
th { background: #7c7bad; color: white; padding: 8px; text-align: left; }
td { padding: 8px; border-bottom: 1px solid #eee; }
code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-size: 13px; }
.warn { background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; padding: 10px 14px; margin-bottom: 16px; }
</style>
</head>
<body>
<h1>REST API Connector \u2014 G\xe9n\xe9rateur de requ\xeates</h1>
<p>G\xe9n\xe8re des commandes curl pour l\u2019API REST Odoo.</p>
<div class="warn"><strong>Cl\xe9 API :</strong> Param\xe8tres \u2192 Technique \u2192 Param\xe8tres syst\xe8me \u2192 <code>rest_api_connector.api_key</code></div>

<h2>G\xe9n\xe9rateur</h2>
<div class="box">
  <div class="row">
    <div>
      <label>Ressource</label>
      <select id="gen-resource" onchange="genUpdate()">
        <option value="companies">Entreprises</option>
        <option value="contacts">Contacts</option>
        <option value="crm/leads">Opportunit\xe9s CRM</option>
      </select>
    </div>
    <div>
      <label>M\xe9thode</label>
      <select id="gen-method" onchange="genUpdate()">
        <option value="GET">GET \u2014 Lister / Chercher</option>
        <option value="GET_ID">GET /{id} \u2014 D\xe9tail</option>
        <option value="POST">POST \u2014 Cr\xe9er</option>
        <option value="PUT">PUT /{id} \u2014 Mettre \xe0 jour</option>
        <option value="DELETE">DELETE /{id} \u2014 Archiver</option>
      </select>
    </div>
    <div>
      <label>Cl\xe9 API</label>
      <input type="text" id="gen-key" value="rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" oninput="genUpdate()">
    </div>
  </div>

  <div id="gen-filters-section">
    <label>Filtres <small style="font-weight:normal;color:#888;">(double underscore __ pour les op\xe9rateurs)</small></label>
    <div id="gen-filters"></div>
    <button class="btn-add" onclick="addFilter()">+ Ajouter un filtre</button>
    <div class="row" style="max-width:300px;">
      <div><label>Limit</label><input type="number" id="gen-limit" value="20" min="1" max="500" oninput="genUpdate()"></div>
      <div><label>Offset</label><input type="number" id="gen-offset" value="0" min="0" oninput="genUpdate()"></div>
    </div>
  </div>

  <div id="gen-id-section" style="display:none;margin-bottom:16px;">
    <label>ID de la ressource</label>
    <input type="number" id="gen-id" placeholder="ex: 42" style="max-width:150px;" oninput="genUpdate()">
  </div>

  <div id="gen-body-section" style="display:none;margin-bottom:16px;">
    <label>Corps JSON</label>
    <textarea id="gen-body" rows="10" oninput="genUpdate()" placeholder='{"name": "Ma Soci\xe9t\xe9"}'></textarea>
    <button class="btn-preset" id="gen-preset-btn" onclick="loadPreset()">Charger exemple</button>
  </div>

  <label>Requ\xeate g\xe9n\xe9r\xe9e</label>
  <div class="pre-wrap">
    <pre id="gen-output"></pre>
    <button class="btn-copy" onclick="copyGen()" id="copy-btn">\U0001f4cb Copier</button>
  </div>
</div>

<h2>R\xe9f\xe9rence des filtres</h2>
<table>
  <thead><tr><th>Syntaxe</th><th>Op\xe9rateur</th><th>Exemple</th></tr></thead>
  <tbody>
    <tr><td><code>champ=valeur</code></td><td>\xc9galit\xe9 exacte</td><td><code>city=Paris</code> / <code>stage_id=3</code></td></tr>
    <tr><td><code>champ__like=valeur</code></td><td>Contient (ilike)</td><td><code>name__like=veolia</code> / <code>partner_name__like=veolia</code></td></tr>
    <tr><td><code>champ__gte=valeur</code></td><td>&ge; sup\xe9rieur ou \xe9gal</td><td><code>expected_revenue__gte=1000</code></td></tr>
    <tr><td><code>champ__lte=valeur</code></td><td>&le; inf\xe9rieur ou \xe9gal</td><td><code>expected_revenue__lte=5000</code></td></tr>
    <tr><td><code>created_after=YYYY-MM-DD</code></td><td>Cr\xe9\xe9 apr\xe8s (CRM)</td><td><code>created_after=2026-01-01</code></td></tr>
    <tr><td><code>created_before=YYYY-MM-DD</code></td><td>Cr\xe9\xe9 avant (CRM)</td><td><code>created_before=2026-12-31</code></td></tr>
    <tr><td><code>updated_after=YYYY-MM-DD</code></td><td>Modifi\xe9 apr\xe8s (CRM)</td><td><code>updated_after=2026-07-01</code></td></tr>
    <tr><td><code>limit=N</code></td><td>Nb r\xe9sultats (max 500)</td><td><code>limit=50</code> \u2014 d\xe9faut 100</td></tr>
    <tr><td><code>offset=N</code></td><td>Pagination</td><td><code>offset=100</code></td></tr>
  </tbody>
</table>

<h2>Champs disponibles</h2>
<details>
  <summary>Entreprises \u2014 /api/v1/companies</summary>
  <table><thead><tr><th>Champ</th><th>Type</th><th>Notes</th></tr></thead><tbody>
    <tr><td><code>name</code></td><td>texte</td><td>Obligatoire \xe0 la cr\xe9ation</td></tr>
    <tr><td><code>email</code></td><td>texte</td><td></td></tr>
    <tr><td><code>phone</code> / <code>mobile</code></td><td>texte</td><td></td></tr>
    <tr><td><code>website</code></td><td>texte</td><td></td></tr>
    <tr><td><code>vat</code></td><td>texte</td><td>TVA intracommunautaire</td></tr>
    <tr><td><code>siret</code></td><td>texte</td><td></td></tr>
    <tr><td><code>street</code> / <code>city</code> / <code>zip</code></td><td>texte</td><td></td></tr>
    <tr><td><code>country_id</code></td><td>entier (ID)</td><td>75 = France</td></tr>
    <tr><td><code>lang</code></td><td>texte</td><td>ex: fr_FR</td></tr>
    <tr><td><code>active</code></td><td>bool\xe9en</td><td>true / false</td></tr>
  </tbody></table>
</details>
<details>
  <summary>Contacts \u2014 /api/v1/contacts</summary>
  <table><thead><tr><th>Champ</th><th>Type</th><th>Notes</th></tr></thead><tbody>
    <tr><td><code>name</code></td><td>texte</td><td>Obligatoire \xe0 la cr\xe9ation</td></tr>
    <tr><td><code>parent_id</code></td><td>entier (ID)</td><td>ID de l\u2019entreprise li\xe9e</td></tr>
    <tr><td><code>email</code></td><td>texte</td><td></td></tr>
    <tr><td><code>phone</code> / <code>mobile</code></td><td>texte</td><td></td></tr>
    <tr><td><code>function</code></td><td>texte</td><td>Poste / fonction</td></tr>
    <tr><td><code>type</code></td><td>texte</td><td>contact, invoice, delivery, other</td></tr>
    <tr><td><code>street</code> / <code>city</code> / <code>zip</code></td><td>texte</td><td></td></tr>
    <tr><td><code>country_id</code></td><td>entier (ID)</td><td>75 = France</td></tr>
  </tbody></table>
</details>
<details>
  <summary>Opportunit\xe9s CRM \u2014 /api/v1/crm/leads</summary>
  <table><thead><tr><th>Champ</th><th>Type</th><th>Notes</th></tr></thead><tbody>
    <tr><td><code>name</code></td><td>texte</td><td>Titre \u2014 obligatoire</td></tr>
    <tr><td><code>partner_id</code></td><td>entier (ID)</td><td>ID entreprise li\xe9e</td></tr>
    <tr><td><code>partner_name</code></td><td>texte</td><td>Filtrable avec <code>partner_name__like=veolia</code></td></tr>
    <tr><td><code>stage_id</code></td><td>entier (ID)</td><td>\xc9tape du pipeline</td></tr>
    <tr><td><code>user_id</code></td><td>entier (ID)</td><td>Commercial assign\xe9</td></tr>
    <tr><td><code>team_id</code></td><td>entier (ID)</td><td>\xc9quipe commerciale</td></tr>
    <tr><td><code>expected_revenue</code></td><td>d\xe9cimal</td><td></td></tr>
    <tr><td><code>probability</code></td><td>d\xe9cimal</td><td>0 \xe0 100</td></tr>
    <tr><td><code>date_deadline</code></td><td>date</td><td>Format YYYY-MM-DD</td></tr>
    <tr><td><code>tag_ids</code></td><td>liste d\u2019IDs</td><td>ex: [1, 2, 3]</td></tr>
    <tr><td><code>x_participants</code></td><td>entier</td><td>Nombre de stagiaires</td></tr>
    <tr><td><code>x_date_debut</code> / <code>x_date_fin</code></td><td>date</td><td>Format YYYY-MM-DD</td></tr>
    <tr><td><code>x_nb_heures</code></td><td>d\xe9cimal</td><td>Dur\xe9e de la formation</td></tr>
    <tr><td><code>x_contact_id</code></td><td>entier (ID)</td><td>Contact client li\xe9</td></tr>
    <tr><td><code>x_stagiaires</code> / <code>x_stagiaires_emails</code></td><td>texte</td><td></td></tr>
  </tbody></table>
</details>

<script>
var BASE = 'https://odoo.webanalyste.com';
var PRESETS = {
  companies: {
    POST: '{\\n  "name": "Ma Soci\\u00e9t\\u00e9",\\n  "email": "contact@masociete.fr",\\n  "phone": "01 23 45 67 89",\\n  "city": "Paris",\\n  "zip": "75001",\\n  "country_id": 75\\n}',
    PUT:  '{\\n  "phone": "01 99 88 77 66",\\n  "website": "https://masociete.fr"\\n}'
  },
  contacts: {
    POST: '{\\n  "name": "Jean Dupont",\\n  "email": "jean.dupont@masociete.fr",\\n  "phone": "06 12 34 56 78",\\n  "function": "Directeur Commercial",\\n  "parent_id": 42,\\n  "type": "contact"\\n}',
    PUT:  '{\\n  "email": "nouveau@email.fr",\\n  "mobile": "07 98 76 54 32"\\n}'
  },
  'crm/leads': {
    POST: '{\\n  "name": "Formation React - Ma Soci\\u00e9t\\u00e9",\\n  "partner_id": 42,\\n  "stage_id": 1,\\n  "expected_revenue": 3500.0,\\n  "x_participants": 8,\\n  "x_date_debut": "2026-09-15",\\n  "x_nb_heures": 35.0\\n}',
    PUT:  '{\\n  "stage_id": 4,\\n  "expected_revenue": 4200.0,\\n  "probability": 80\\n}'
  }
};

function addFilter() {
  var c = document.getElementById('gen-filters');
  var row = document.createElement('div');
  row.className = 'filter-row';
  var i1 = document.createElement('input'); i1.type='text'; i1.placeholder='champ  ex: name, city, partner_name'; i1.oninput=genUpdate;
  var s = document.createElement('select'); s.onchange=genUpdate;
  [['eq','= \u00e9gal'],['like','__like contient'],['gte','__gte >='],['lte','__lte <=']].forEach(function(o){var op=document.createElement('option');op.value=o[0];op.textContent=o[1];s.appendChild(op);});
  var i2 = document.createElement('input'); i2.type='text'; i2.placeholder='valeur'; i2.oninput=genUpdate;
  var b = document.createElement('button'); b.className='btn-remove'; b.textContent='\u2715'; b.onclick=function(){row.remove();genUpdate();};
  row.appendChild(i1); row.appendChild(s); row.appendChild(i2); row.appendChild(b);
  c.appendChild(row); genUpdate();
}

function loadPreset() {
  var r=document.getElementById('gen-resource').value, m=document.getElementById('gen-method').value;
  var p=(PRESETS[r]||{})[m]||'';
  if(p){document.getElementById('gen-body').value=JSON.parse('"'+p+'"');genUpdate();}
}

function genUpdate() {
  var resource=document.getElementById('gen-resource').value;
  var method=document.getElementById('gen-method').value;
  var key=document.getElementById('gen-key').value.trim()||'VOTRE_CLE';
  var isGet=method==='GET', isGetId=method==='GET_ID', isPost=method==='POST', isPut=method==='PUT', isDel=method==='DELETE';
  document.getElementById('gen-filters-section').style.display=isGet?'':'none';
  document.getElementById('gen-id-section').style.display=(isGetId||isPut||isDel)?'':'none';
  document.getElementById('gen-body-section').style.display=(isPost||isPut)?'':'none';
  var pb=document.getElementById('gen-preset-btn');
  pb.style.display=((isPost||isPut)&&(PRESETS[resource]||{})[method])?'':'none';
  var id=(document.getElementById('gen-id').value||'').trim();
  var limit=document.getElementById('gen-limit').value;
  var offset=document.getElementById('gen-offset').value;
  var httpMethod=isGetId?'GET':method;
  var url=BASE+'/api/v1/'+resource;
  if(isGetId||isPut||isDel) url+='/'+(id||'{id}');
  var params=[];
  if(isGet){
    document.querySelectorAll('#gen-filters .filter-row').forEach(function(row){
      var inputs=row.querySelectorAll('input');
      var sel=row.querySelector('select');
      var field=inputs[0].value.trim(), op=sel.value, val=inputs[1].value.trim();
      if(field&&val){var k=op==='eq'?field:field+'__'+(op==='like'?'like':op);params.push(encodeURIComponent(k)+'='+encodeURIComponent(val));}
    });
    if(limit&&parseInt(limit)!==100) params.push('limit='+limit);
    if(offset&&parseInt(offset)!==0) params.push('offset='+offset);
    if(params.length) url+='?'+params.join('&');
  }
  var body=(isPost||isPut)?(document.getElementById('gen-body').value||'').trim():'';
  var lines=['curl -s \\\\'];
  lines.push('  -H "X-API-Key: '+key+'" \\\\');
  if(httpMethod!=='GET') lines.push('  -X '+httpMethod+' \\\\');
  if(body) lines.push('  -H "Content-Type: application/json" \\\\');
  if(body) lines.push("  -d '"+body+"' \\\\");
  lines.push('  "'+url+'" | jq');
  document.getElementById('gen-output').textContent=lines.join('\\n');
}

function copyGen(){
  var text=document.getElementById('gen-output').textContent.replace(/\\\\\\\\/g,'\\\\');
  navigator.clipboard.writeText(text).then(function(){
    var b=document.getElementById('copy-btn'); b.textContent='\u2705 Copi\u00e9 !';
    setTimeout(function(){b.textContent='\U0001f4cb Copier';},2000);
  });
}
addFilter();
</script>
</body></html>"""
        return Response(html, content_type='text/html;charset=utf-8')
