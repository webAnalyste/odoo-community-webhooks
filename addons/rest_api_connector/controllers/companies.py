from odoo import http
from odoo.http import request

from .auth import require_api_key, json_response, _error, parse_body, build_domain, get_raw_params

COMPANY_FIELDS = {
    'name': 'char',
    'email': 'char',
    'phone': 'char',
    'mobile': 'char',
    'website': 'char',
    'vat': 'char',
    'siret': 'char',
    'street': 'char',
    'street2': 'char',
    'city': 'char',
    'zip': 'char',
    'country_id': 'many2one',
    'state_id': 'many2one',
    'lang': 'char',
    'active': 'boolean',
}

WRITABLE_FIELDS = list(COMPANY_FIELDS.keys())


def _serialize(company):
    return {
        'id': company.id,
        'name': company.name,
        'email': company.email,
        'phone': company.phone,
        'mobile': company.mobile,
        'website': company.website,
        'vat': company.vat,
        'siret': company.siret if hasattr(company, 'siret') else None,
        'street': company.street,
        'street2': company.street2,
        'city': company.city,
        'zip': company.zip,
        'country_id': company.country_id.id if company.country_id else None,
        'country_name': company.country_id.name if company.country_id else None,
        'state_id': company.state_id.id if company.state_id else None,
        'state_name': company.state_id.name if company.state_id else None,
        'lang': company.lang,
        'active': company.active,
        'contact_count': len(company.child_ids),
    }


class CompaniesController(http.Controller):

    @http.route('/api/v1/companies', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def list_companies(self, **kwargs):
        params = get_raw_params()
        limit = min(int(params.get('limit', 100)), 500)
        offset = int(params.get('offset', 0))
        domain = [('is_company', '=', True), ('active', 'in', [True, False])]
        domain += build_domain(COMPANY_FIELDS, params)

        companies = request.env['res.partner'].sudo().search(domain, limit=limit, offset=offset)
        total = request.env['res.partner'].sudo().search_count(domain)

        return json_response({
            'total': total,
            'limit': limit,
            'offset': offset,
            'results': [_serialize(c) for c in companies],
        })

    @http.route('/api/v1/companies/<int:company_id>', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def get_company(self, company_id, **kwargs):
        company = request.env['res.partner'].sudo().browse(company_id)
        if not company.exists() or not company.is_company:
            return _error(404, 'Company not found')
        return json_response(_serialize(company))

    @http.route('/api/v1/companies', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def create_company(self, **kwargs):
        vals = parse_body()
        if not vals.get('name'):
            return _error(400, 'name is required')
        vals['is_company'] = True
        vals.pop('id', None)
        vals = {k: v for k, v in vals.items() if k in WRITABLE_FIELDS + ['is_company']}
        company = request.env['res.partner'].sudo().create(vals)
        return json_response(_serialize(company), status=201)

    @http.route('/api/v1/companies/<int:company_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    @require_api_key
    def update_company(self, company_id, **kwargs):
        company = request.env['res.partner'].sudo().browse(company_id)
        if not company.exists() or not company.is_company:
            return _error(404, 'Company not found')
        vals = parse_body()
        vals.pop('id', None)
        vals.pop('is_company', None)
        vals = {k: v for k, v in vals.items() if k in WRITABLE_FIELDS}
        if not vals:
            return _error(400, 'No valid fields to update')
        company.write(vals)
        return json_response(_serialize(company))

    @http.route('/api/v1/companies/<int:company_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    @require_api_key
    def archive_company(self, company_id, **kwargs):
        company = request.env['res.partner'].sudo().browse(company_id)
        if not company.exists() or not company.is_company:
            return _error(404, 'Company not found')
        company.write({'active': False})
        return json_response({'success': True, 'id': company_id})
