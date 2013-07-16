from flask import url_for, current_app, request, session, flash
from werkzeug import LocalProxy

_flack = LocalProxy(lambda: current_app.extensions['flack'])

def get_url(endpoint_or_url):
    try:
        return url_for(endpoint_or_url)
    except:
        return endpoint_or_url

def get_post_action_redirect(config_key):
    return (get_url(request.args.get('next')) or
            get_url(request.form.get('next')) or
            find_redirect(config_key))

def get_post_feedback_redirect():
    return get_post_action_redirect('FLACK_DEFAULT_FEEDBACK_RETURN_URL')

def find_redirect(key):
    rv = (get_url(session.pop(key.lower(), None)) or
          get_url(current_app.config[key.upper()] or None) or '/')
    return rv

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

def config_value(key, app=None, default=None):
    app = app or current_app
    return get_config(app).get(key.upper(), default)

def do_flash(message, category=None):
    if config_value('FLASH_MESSAGES'):
        flash(message, category)

def set_form_next(form):
    if getattr(form, 'next', None):
        form.next.data = get_url(request.args.get('next')) \
            or get_url(request.form.get('next')) or ''
