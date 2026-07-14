from odoo import http
from odoo.http import request

from .auth import require_api_key, json_response, _error, parse_body, build_domain, get_raw_params

CRM_FIELDS = {
    'name': 'char',
    'partner_id': 'many2one',
    'stage_id': 'many2one',
    'user_id': 'many2one',
    'team_id': 'many2one',
    'priority': 'char',
    'probability': 'float',
    'expected_revenue': 'float',
    'description': 'char',
    'email_from': 'char',
    'phone': 'char',
    'mobile': 'char',
    'active': 'boolean',
    'date_deadline': 'char',
    'tag_ids': 'many2many',
    # custom fields
    'x_participants': 'integer',
    'x_date_debut': 'char',
    'x_date_fin': 'char',
    'x_nb_heures': 'float',
    'x_stagiaires': 'char',
    'x_stagiaires_emails': 'char',
    'x_contact_id': 'many2one',
}

WRITABLE_FIELDS = [f for f in CRM_FIELDS if f != 'tag_ids'] + ['tag_ids']


def _serialize(lead):
    return {
        'id': lead.id,
        'name': lead.name,
        'partner_id': lead.partner_id.id if lead.partner_id else None,
        'partner_name': lead.partner_id.name if lead.partner_id else None,
        'stage_id': lead.stage_id.id if lead.stage_id else None,
        'stage_name': lead.stage_id.name if lead.stage_id else None,
        'user_id': lead.user_id.id if lead.user_id else None,
        'user_name': lead.user_id.name if lead.user_id else None,
        'team_id': lead.team_id.id if lead.team_id else None,
        'team_name': lead.team_id.name if lead.team_id else None,
        'priority': lead.priority,
        'probability': lead.probability,
        'expected_revenue': lead.expected_revenue,
        'description': lead.description,
        'email_from': lead.email_from,
        'phone': lead.phone,
        'mobile': lead.mobile,
        'active': lead.active,
        'date_deadline': str(lead.date_deadline) if lead.date_deadline else None,
        'create_date': str(lead.create_date) if lead.create_date else None,
        'write_date': str(lead.write_date) if lead.write_date else None,
        'tag_ids': lead.tag_ids.ids,
        'tag_names': lead.tag_ids.mapped('name'),
        # custom fields
        'x_participants': lead.x_participants if hasattr(lead, 'x_participants') else None,
        'x_date_debut': str(lead.x_date_debut) if hasattr(lead, 'x_date_debut') and lead.x_date_debut else None,
        'x_date_fin': str(lead.x_date_fin) if hasattr(lead, 'x_date_fin') and lead.x_date_fin else None,
        'x_nb_heures': lead.x_nb_heures if hasattr(lead, 'x_nb_heures') else None,
        'x_stagiaires': lead.x_stagiaires if hasattr(lead, 'x_stagiaires') else None,
        'x_stagiaires_emails': lead.x_stagiaires_emails if hasattr(lead, 'x_stagiaires_emails') else None,
        'x_contact_id': lead.x_contact_id.id if hasattr(lead, 'x_contact_id') and lead.x_contact_id else None,
        'x_contact_name': lead.x_contact_id.name if hasattr(lead, 'x_contact_id') and lead.x_contact_id else None,
        'x_contact_email': lead.x_contact_id.email if hasattr(lead, 'x_contact_id') and lead.x_contact_id else None,
    }


def _prepare_vals(vals):
    vals.pop('id', None)
    if 'tag_ids' in vals and isinstance(vals['tag_ids'], list):
        vals['tag_ids'] = [(6, 0, vals['tag_ids'])]
    return {k: v for k, v in vals.items() if k in WRITABLE_FIELDS}


class CrmController(http.Controller):

    @http.route('/api/v1/crm/leads', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def list_leads(self, **kwargs):
        params = get_raw_params()
        limit = min(int(params.get('limit', 100)), 500)
        offset = int(params.get('offset', 0))

        domain = [('active', 'in', [True, False])]

        if params.get('created_after'):
            domain.append(('create_date', '>=', params['created_after']))
        if params.get('created_before'):
            domain.append(('create_date', '<=', params['created_before']))
        if params.get('updated_after'):
            domain.append(('write_date', '>=', params['updated_after']))

        domain += build_domain(CRM_FIELDS, params)

        leads = request.env['crm.lead'].sudo().search(domain, limit=limit, offset=offset, order='create_date desc')
        total = request.env['crm.lead'].sudo().search_count(domain)

        return json_response({
            'total': total,
            'limit': limit,
            'offset': offset,
            'results': [_serialize(l) for l in leads],
        })

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def get_lead(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return _error(404, 'Lead not found')
        return json_response(_serialize(lead))

    @http.route('/api/v1/crm/leads', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def create_lead(self, **kwargs):
        vals = parse_body()
        if not vals.get('name'):
            return _error(400, 'name is required')
        vals = _prepare_vals(vals)
        lead = request.env['crm.lead'].sudo().create(vals)
        return json_response(_serialize(lead), status=201)

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    @require_api_key
    def update_lead(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return _error(404, 'Lead not found')
        vals = parse_body()
        vals = _prepare_vals(vals)
        if not vals:
            return _error(400, 'No valid fields to update')
        lead.write(vals)
        return json_response(_serialize(lead))

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    @require_api_key
    def archive_lead(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return _error(404, 'Lead not found')
        lead.write({'active': False})
        return json_response({'success': True, 'id': lead_id})
