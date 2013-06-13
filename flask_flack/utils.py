from flask import url_for, current_app
from werkzeug import LocalProxy

_flack = LocalProxy(lambda: current_app.extensions['flack'])

def get_config(app):
    items = app.config.items()
    prefix = 'FLACK_'

    def strip_prefix(tup):
        return (tup[0].replace('FLACK_', ''), tup[1])

    return dict([strip_prefix(i) for i in items if i[0].startswith(prefix)])

def get_feedback_endpoint_name(endpoint):
    return '{}.{}'.format(_flack.blueprint_name, endpoint)

def url_for_feedback(endpoint, **values):
    endpoint = get_feedback_endpoint_name(endpoint)
    return url_for(endpoint, **values)

def get_message(key, **kwargs):
    rv = config_value('MSG_' + key)
    return rv[0] % kwargs, rv[1]

def do_flash(message, category=None):
    if config_value('FLASH_MESSAGES'):
        flash(message, category)
