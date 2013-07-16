from flask import current_app, request, get_template_attribute
from werkzeug import LocalProxy
from werkzeug.datastructures import MultiDict
from .forms import InterestForm, ProblemForm, CommentForm
from .views import create_blueprint
from .utils import (get_config, url_for_feedback, set_form_next,
                    config_value as cv)

_flack = LocalProxy(lambda: current_app.extensions['flack'])
_endpoint = LocalProxy(lambda: request.endpoint.rsplit('.')[-1])

_default_config = {
    'BLUEPRINT_NAME': 'feedback',
    'URL_PREFIX': None,
    'SUBDOMAIN': None,
    'FLASH_MESSAGES': True,
    'DEFAULT_FEEDBACK_RETURN_URL': '/',
    'FEEDBACK_URL': '/feedback',
    'INTEREST_URL': '/feedback/interest',
    'PROBLEM_URL': '/feedback/problem',
    'COMMENT_URL': '/feedback/comment',
    'INTEREST_TEMPLATE': 'feedback/interest.html',
    'PROBLEM_TEMPLATE': 'feedback/problem.html',
    'COMMENT_TEMPLATE': 'feedback/comment.html',
    'PRIORITY_CHOICES': [('low', 'low'),
                         ('medium', 'medium'),
                         ('high', 'high'),
                         ('urgent', 'urgent')]
}

_default_messages = {
    'INVALID_REDIRECT': ('Redirections outside the domain are forbidden', 'error'),
    'INTEREST_RESPOND': ("Thank you for your interest!", 'success'),
    'PROBLEM_RESPOND': ("Thank you for submitting your issue.", 'success'),
    'COMMENT_RESPOND': ("Thank you for the feedback!", 'success'),
    'INVALID_EMAIL_ADDRESS': ('Invalid email address', 'error'),
    'EMAIL_NOT_PROVIDED': ('Email not provided', 'error'),
}

_default_forms = {
    'interest_form': (InterestForm, 'feedback/_feedback_macros/_interest.html', 'interest_macro'),
    'problem_form': (ProblemForm, 'feedback/_feedback_macros/_problem.html', 'problem_macro'),
    'comment_form': (CommentForm,'feedback/_feedback_macros/_comment.html', 'comment_macro')
}


def _context_processor():
    return dict(url_for_feedback=url_for_feedback, flack=_flack)


def _get_state(app, datastore, **kwargs):
    for key, value in get_config(app).items():
        kwargs[key.lower()] = value

    updateable = {'app': app,
                  'datastore': datastore,
                  '_context_processors': {}}

    kwargs.update(updateable)

    for key, value in _default_forms.items():
        if key not in kwargs or not kwargs[key]:
            kwargs[key] = value

    return _FeedbackState(**kwargs)


class _Ctx(object):
    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def inline(self):
        return self.macro(self)


class _FeedbackState(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)

    @property
    def _ctx(self):
        ctx = _Ctx(template=self._ctx_template,
                   form=self._ctx_view_form,
                   macro=self._ctx_form_macro)
        if request.json:
            ctx.update(json_ctx=True)
        ctx.update(**self._run_ctx_processor(_endpoint))
        return ctx

    @property
    def _ctx_view_form(self):
        if request.json:
            return self._ctx_form_json
        else:
            return self._ctx_form

    @property
    def _ctx_form_base(self):
        f = getattr(_flack, '{}_form'.format(_endpoint), None)
        if f:
            form = f[0]
            set_form_next(form)
            return form

    @property
    def _ctx_form(self):
        if self._ctx_form_base:
            return self._ctx_form_base(request.form)

    @property
    def _ctx_form_json(self):
        return self._ctx_form_base(MultiDict(request.json))

    def which_macro(self, which):
        return getattr(self, '{}_form'.format(which), None)

    @property
    def _ctx_form_macro(self):
        m = self.which_macro(_endpoint)
        if m:
            mform, mwhere, mname = m[0], m[1], m[2]
            return get_template_attribute(mwhere, mname)

    def inline_form(self, which, form=None, ctx=None):
        """
        Inline a form inside any template

        :param which: which macro to use, where there is a corresponding
        configuration variable e.g. specify 'login' where
        config value 'login_form' exists(see _default_forms
        above)
        :param form: optional, designate a specific form to use within
        the macro
        :param ctx: optional, a dict with specific context variables to use

        e.g. within in a another template

        {{ security.inline_form('change_password') }}

        or

        {{ security.inline_form('login', MyLoginForm, {'myvar': 12345}) }}
        """
        m = self.which_macro(which)
        if m:
            mform, mwhere, mname = m[0], m[1], m[2]
            t = get_template_attribute(mwhere, mname)
            t_ctx = _Ctx()
            t_ctx.update(**self._run_ctx_processor(_endpoint))
            t_ctx.update(macro=t)
            if form:
                t_ctx.update(form=form(request.form))
            else:
                t_ctx.update(form=m[0](request.form))
            if ctx:
                t_ctx.update(**ctx)
            return t(t_ctx)

    @property
    def _ctx_template(self):
        return cv('{}_TEMPLATE'.format(_endpoint))

    def _add_ctx_processor(self, endpoint, fn):
        group = self._context_processors.setdefault(endpoint, [])
        fn not in group and group.append(fn)

    def _run_ctx_processor(self, endpoint):
        rv, fns = {}, []
        for g in [None, endpoint]:
            for fn in self._context_processors.setdefault(g, []):
                rv.update(fn())
        return rv

    def context_processor(self, fn):
        self._add_ctx_processor(None, fn)

    def feedback_context_processor(self, fn):
        self._add_ctx_processor('feedback', fn)

    def interest_context_processor(self, fn):
        self._add_ctx_processor('interest', fn)

    def problem_context_processor(self, fn):
        self._add_ctx_processor('problem', fn)

    def comment_context_processor(self, fn):
        self._add_ctx_processor('comment', fn)


class Flack(object):
    def __init__(self, app=None, datastore=None, **kwargs):
        self.app = app
        self.datastore = datastore

        if app is not None and datastore is not None:
            self._state = self.init_app(app, datastore, **kwargs)

    def init_app(self,
                 app,
                 datastore=None,
                 register_blueprint=True,
                 interest_form=None,
                 problem_form=None,
                 comment_form=None):
        datastore = datastore or self.datastore

        for key, value in _default_config.items():
            app.config.setdefault('FLACK_{}'.format(key), value)

        for key, value in _default_messages.items():
            app.config.setdefault('FLACK_MSG_{}'.format(key), value)

        state = _get_state(app, datastore,
                           interest_form=interest_form,
                           problem_form=problem_form,
                           comment_form=comment_form)

        if register_blueprint:
            app.register_blueprint(create_blueprint(state, __name__))
            self.register_context_processors(app, _context_processor())

        app.extensions['flack'] = state

        return state

    def register_context_processors(self, app, context_processors):
        app.jinja_env.globals.update(context_processors)

    def __getattr__(self, name):
        return getattr(self._state, name, None)
