from odoo import http
from odoo.http import request

from .auth import require_api_key, json_response, _error, parse_body, build_domain, get_raw_params

CONTACT_FIELDS = {
    'name': 'char',
    'email': 'char',
    'phone': 'char',
    'mobile': 'char',
    'function': 'char',
    'street': 'char',
    'street2': 'char',
    'city': 'char',
    'zip': 'char',
    'country_id': 'many2one',
    'state_id': 'many2one',
    'parent_id': 'many2one',
    'type': 'char',
    'active': 'boolean',
    'comment': 'char',
}

WRITABLE_FIELDS = list(CONTACT_FIELDS.keys())


def _serialize(contact):
    return {
        'id': contact.id,
        'name': contact.name,
        'email': contact.email,
        'phone': contact.phone,
        'mobile': contact.mobile,
        'function': contact.function,
        'street': contact.street,
        'street2': contact.street2,
        'city': contact.city,
        'zip': contact.zip,
        'country_id': contact.country_id.id if contact.country_id else None,
        'country_name': contact.country_id.name if contact.country_id else None,
        'state_id': contact.state_id.id if contact.state_id else None,
        'parent_id': contact.parent_id.id if contact.parent_id else None,
        'parent_name': contact.parent_id.name if contact.parent_id else None,
        'type': contact.type,
        'active': contact.active,
        'comment': contact.comment,
    }


class ContactsController(http.Controller):

    @http.route('/api/v1/contacts', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def list_contacts(self, **kwargs):
        params = get_raw_params()
        limit = min(int(params.get('limit', 100)), 500)
        offset = int(params.get('offset', 0))
        domain = [('is_company', '=', False), ('active', 'in', [True, False])]
        domain += build_domain(CONTACT_FIELDS, params)

        contacts = request.env['res.partner'].sudo().search(domain, limit=limit, offset=offset)
        total = request.env['res.partner'].sudo().search_count(domain)

        return json_response({
            'total': total,
            'limit': limit,
            'offset': offset,
            'results': [_serialize(c) for c in contacts],
        })

    @http.route('/api/v1/contacts/<int:contact_id>', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def get_contact(self, contact_id, **kwargs):
        contact = request.env['res.partner'].sudo().browse(contact_id)
        if not contact.exists() or contact.is_company:
            return _error(404, 'Contact not found')
        return json_response(_serialize(contact))

    @http.route('/api/v1/contacts', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def create_contact(self, **kwargs):
        vals = parse_body()
        if not vals.get('name'):
            return _error(400, 'name is required')
        vals['is_company'] = False
        vals.pop('id', None)
        vals = {k: v for k, v in vals.items() if k in WRITABLE_FIELDS + ['is_company']}
        contact = request.env['res.partner'].sudo().create(vals)
        return json_response(_serialize(contact), status=201)

    @http.route('/api/v1/contacts/<int:contact_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    @require_api_key
    def update_contact(self, contact_id, **kwargs):
        contact = request.env['res.partner'].sudo().browse(contact_id)
        if not contact.exists() or contact.is_company:
            return _error(404, 'Contact not found')
        vals = parse_body()
        vals.pop('id', None)
        vals.pop('is_company', None)
        vals = {k: v for k, v in vals.items() if k in WRITABLE_FIELDS}
        if not vals:
            return _error(400, 'No valid fields to update')
        contact.write(vals)
        return json_response(_serialize(contact))

    @http.route('/api/v1/contacts/<int:contact_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    @require_api_key
    def archive_contact(self, contact_id, **kwargs):
        contact = request.env['res.partner'].sudo().browse(contact_id)
        if not contact.exists() or contact.is_company:
            return _error(404, 'Contact not found')
        contact.write({'active': False})
        return json_response({'success': True, 'id': contact_id})
