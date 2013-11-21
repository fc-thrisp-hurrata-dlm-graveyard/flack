import re
from functools import partial
from flask import current_app, request, get_template_attribute
from werkzeug import LocalProxy
from werkzeug.datastructures import MultiDict
from .forms import FeedbackForm, ProblemsForm
from .views import create_blueprint
from .utils import (get_config, url_for_feedback, set_form_next,
                    config_value as cv)


kwarg_is_form = re.compile(".*_form\Z")

_feedback = LocalProxy(lambda: current_app.extensions['feedback'])

_endpoint = LocalProxy(lambda: request.endpoint.rsplit('.')[-1])

_default_config = {
    'BLUEPRINT_NAME': 'feedback',
    'URL_PREFIX': None,
    'SUBDOMAIN': None,
    'FLASH_MESSAGES': True,
    'DEFAULT_FEEDBACK_RETURN_URL': '/',
    'FEEDBACK_URL': '/feedback',
    'DEFAULT_FEEDBACK_TEMPLATE': 'feedback/feedback.html',
    'PRIORITY_CHOICES': {'options': [('low', 'low'), ('medium', 'medium'), ('high', 'high'), ('urgent', 'urgent')],
                         'default': 'low'},
    'SUBMIT_TEXT': 'submit'
}

_default_messages = {
    'INVALID_REDIRECT': ('Redirections outside the domain are forbidden', 'error'),
    'FEEDBACK_RESPOND': ("Thank you for the feedback!", 'success'),
    'INVALID_EMAIL_ADDRESS': ('Invalid email address', 'error'),
    'EMAIL_NOT_PROVIDED': ('Email not provided', 'error'),
}

_feedback_forms = {
    'feedback_form': FeedbackForm,
    'problems_form': ProblemsForm
}


def add_feedback_forms(**kwargs):
    for k,v in kwargs.items():
        if kwarg_is_form.match(k):
            _feedback_forms.update({k: v})


def update_feedback_forms(**kwargs):
    for key, value in _feedback_forms.items():
        if kwargs.get(key):
            _feedback_forms.update({key: kwargs[key]})


def _context_processor(state):
    ctx_prcs = {}
    ctx_prcs.update({'url_for_feedback': url_for_feedback, 'feedback':_feedback})
    for k,v in _feedback_forms.items():
        ctx_prcs.update({k: partial(state.form_macro, v)})
    return ctx_prcs


def _get_state(app, datastore, **kwargs):
    for key, value in get_config(app).items():
        kwargs[key.lower()] = value

    kwargs.update({'app': app,
                   'datastore': datastore,
                   '_ctxs': {}})

    add_feedback_forms(**kwargs)
    update_feedback_forms(**kwargs)

    kwargs.update(_feedback_forms)

    return _FeedbackState(**kwargs)


class _FeedbackState(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)

    @property
    def _ctx(self):
        return self._run_ctx(self._feedback_endpoint)

    def _add_ctx(self, endpoint, fn):
        group = self._ctxs.setdefault(endpoint, [])
        fn not in group and group.append(fn)

    def _run_ctx(self, endpoint):
        rv, fns = {}, []
        for g in [None, endpoint]:
            for fn in self._ctxs.setdefault(g, []):
                rv.update(fn())
        return rv

    def get_fn_name(self, name):
        if name.partition('_')[0] == 'security':
            return None
        else:
            return name.rpartition('_')[0]

    def add_ctx(self, fn):
        self._add_ctx(self.get_fn_name(fn.__name__), fn)

    @property
    def current_form(self):
        return _feedback_forms.get("{}_form".format(self._feedback_point))

    @property
    def current_template(self):
        return getattr(self.current_form, 'template', cv("default_feedback_template"))

    @property
    def _feedback_point(self):
        return request.values.get('instance', 'feedback')

    def form_macro(self, form):
        form_is = partial(self._form_is, form)
        run_ctx = partial(self._run_ctx, self._feedback_endpoint)
        return self._on_form(form_is, run_ctx)

    def _form_is(self, form):
        if request.json:
            return form(MultiDict(request.json))
        else:
            return form(request.form)

    def _on_form(self, form_is, run_ctx):
        f = form_is()
        if request.form:
            f.validate()
        return f.macro_render(run_ctx())


class Flack(object):
    def __init__(self, app=None, datastore=None, **kwargs):
        self.app = app
        self.datastore = datastore

        if app is not None and datastore is not None:
            self._state = self.init_app(app, datastore, **kwargs)

    def init_app(self, app, datastore=None, register_blueprint=True, **kwargs):
        """Intializes the Flask-Flack extension for the specified
        application and datastore implentation.
        """
        datastore = datastore or self.datastore

        for key, value in _default_config.items():
            app.config.setdefault('FLACK_{}'.format(key), value)

        for key, value in _default_messages.items():
            app.config.setdefault('FLACK_MSG_{}'.format(key), value)

        state = _get_state(app, datastore, **kwargs)

        if register_blueprint:
            app.register_blueprint(create_blueprint(state, __name__))

        app.extensions['feedback'] = state

        self.register_context_processors(app, _context_processor(state))

        return state

    def register_context_processors(self, app, context_processors):
        app.jinja_env.globals.update(context_processors)

    def __getattr__(self, name):
        return getattr(self._state, name, None)
