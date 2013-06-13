from flask import current_app
from werkzeug import LocalProxy
from .forms import InterestForm, ProblemForm, CommentForm
from .views import create_blueprint
from .utils import get_config, url_for_feedback

_flack = LocalProxy(lambda: current_app.extensions['flack'])

_default_config = {
        'BLUEPRINT_NAME': 'feedback',
        'URL_PREFIX': None,
        'SUBDOMAIN': None,
        'FLASH_MESSAGES': True,
        'FEEDBACK_URL': '/feedback',
        'INTEREST_URL': '/feedback/interest',
        'PROBLEM_URL': '/feedback/problem',
        'COMMENT_URL': '/feedback/comment',
        'INTEREST_TEMPLATE': 'feedback/interest.html',
        'PROBLEM_TEMPLATE': 'feedback/problem.html',
        'COMMENT_TEMPLATE': 'feedback/comment.html'
}

_default_messages = {
        'INVALID_REDIRECT': ('Redirections outside the domain are forbidden', 'error'),
        'DEFAULT': ("Thank you for your input.", 'info'),
        'INTEREST_RESPOND': ("Thank you for your interest!", 'success'),
        'PROBLEM_RESPOND': ("Thank you for submitting your issue.", 'success'),
        'COMMENT_RESPOND': ("Thank you for the feedback!", 'success'),
        'INVALID_EMAIL_ADDRESS': ('Invalid email address', 'error'),
        'EMAIL_NOT_PROVIDED': ('Email not provided', 'error'),
}

_default_forms = {
        'interest_form': InterestForm,
        'problem_form': ProblemForm,
        'comment_form': CommentForm
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


class _FeedbackState(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)

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
            app.context_processor(_context_processor)

        app.extensions['flack'] = state

        return state

    def __getattr__(self, name):
        return getattr(self._state, name, None)
