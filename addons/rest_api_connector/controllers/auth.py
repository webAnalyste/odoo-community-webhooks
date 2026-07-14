import json
from functools import wraps

from odoo.http import request


def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        api_key = request.httprequest.headers.get('X-API-Key', '').strip()
        if not api_key:
            return _error(401, 'Missing X-API-Key header')
        expected = request.env['ir.config_parameter'].sudo().get_param(
            'rest_api_connector.api_key'
        )
        if not expected or api_key != expected:
            return _error(403, 'Invalid API key')
        return fn(*args, **kwargs)
    return wrapper


def json_response(data, status=200):
    return request.make_response(
        json.dumps(data, default=str),
        headers=[('Content-Type', 'application/json')],
        status=status,
    )


def _error(status, message):
    return json_response({'error': message}, status=status)


def parse_body():
    try:
        return json.loads(request.httprequest.data or '{}')
    except (ValueError, TypeError):
        return {}


def get_raw_params():
    """Retourne les query params bruts depuis Werkzeug, sans traitement Odoo."""
    return dict(request.httprequest.args)


# Alias de champs : param API -> champ ORM réel
FIELD_ALIASES = {
    'partner_name': 'partner_id.name',
    'company_name': 'parent_id.name',
    'stage_name': 'stage_id.name',
    'user_name': 'user_id.name',
    'team_name': 'team_id.name',
    'country_name': 'country_id.name',
}

_SKIP = {'limit', 'offset', 'created_after', 'created_before', 'updated_after'}


def build_domain(model_fields, params):
    """Construit un domain Odoo depuis les query params bruts."""
    domain = []
    for key, value in params.items():
        if key in _SKIP:
            continue
        if key.endswith('__like'):
            raw = key[:-6]
            fname = FIELD_ALIASES.get(raw, raw)
            domain.append((fname, 'ilike', value))
        elif key.endswith('__gte'):
            raw = key[:-5]
            fname = FIELD_ALIASES.get(raw, raw)
            domain.append((fname, '>=', value))
        elif key.endswith('__lte'):
            raw = key[:-5]
            fname = FIELD_ALIASES.get(raw, raw)
            domain.append((fname, '<=', value))
        else:
            fname = FIELD_ALIASES.get(key, key)
            field_type = model_fields.get(key, 'char')
            if field_type in ('integer', 'many2one'):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass
            elif field_type == 'boolean':
                value = value.lower() in ('1', 'true', 'yes')
            elif field_type == 'float':
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    pass
            domain.append((fname, '=', value))
    return domain
