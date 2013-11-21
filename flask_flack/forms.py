import sys
import inspect

PY2 = sys.version_info[0] == 2
if PY2:
    import urlparse
else:
    import urllib.parse

import flask_wtf as wtf
from flask import request, current_app, get_template_attribute
from flask_wtf import Form as BaseForm
from wtforms import TextAreaField, SelectField, TextField,\
    SubmitField, HiddenField, ValidationError, Field
from wtforms.validators import Required, Email
from werkzeug import LocalProxy
from .utils import get_message, config_value

_datastore = LocalProxy(lambda: current_app.extensions['feedback'].datastore)

_default_choices = LocalProxy(lambda: config_value('priority_choices')['options'])
_default_choices_default = LocalProxy(lambda: config_value('priority_choices')['default'])
_default_submit_text = LocalProxy(lambda: config_value('submit_text'))


class ValidatorMixin(object):
    def __call__(self, form, field):
        if self.message and self.message.isupper():
            self.message = get_message(self.message)[0]
        return super(ValidatorMixin, self).__call__(form, field)


class Required(ValidatorMixin, Required):
    pass


class Email(ValidatorMixin, Email):
    pass


email_required = Required(message='EMAIL_NOT_PROVIDED')
email_validator = Email(message='INVALID_EMAIL_ADDRESS')


class NextFormMixin():
    next = HiddenField()

    def validate_next(self, field):
        url_next = urlparse.urlsplit(field.data)
        url_base = urlparse.urlsplit(request.host_url)
        if url_next.netloc and url_next.netloc != url_base.netloc:
            field.data = ''
            raise ValidationError(get_message('INVALID_REDIRECT')[0])


class EmailFormMixin():
    feedback_email = TextField('feedback_email', validators=[email_required, email_validator])


class PriorityFormMixin():
    feedback_priority = SelectField('feedback_priority', choices=_default_choices, default=_default_choices_default)


class SubmitFormMixin():
    submit = SubmitField(_default_submit_text)


class FeedbackForm(EmailFormMixin, SubmitFormMixin, BaseForm):
    template = 'feedback/feedback.html',
    mname = 'feedback_macro'
    mtemplate = 'feedback/_feedback_macros/_feedback.html'

    feedback_tag = HiddenField("feedback_tag")
    feedback_content = TextAreaField('feedback_content')

    def __init__(self, *args, **kwargs):
        if current_app.testing:
            self.TIME_LIMIT = None
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.instance_tag = 'feedback'

    def update(self, ctx):
        [setattr(self, k, v) for k,v in ctx.items()]

    def to_dict(form):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and \
                hasattr(_datastore.feedback_model, member.name)

        fields = inspect.getmembers(form, is_field_and_user_attr)
        return dict((k, v.data) for k, v in fields)

    @property
    def _macro_renderable(self):
        return get_template_attribute(self.mtemplate, self.mname)

    def macro_render(self, ctx):
        self.update(ctx)
        return self._macro_renderable(self)

    def validate(self):
        if not super(FeedbackForm, self).validate():
            return False
        return True


class ProblemsForm(PriorityFormMixin, FeedbackForm):
    template = 'feedback/problems.html',
    mname = 'problems_macro'
    mtemplate = 'feedback/_feedback_macros/_feedback.html'

    def __init__(self, *args, **kwargs):
        super(ProblemsForm, self).__init__(*args, **kwargs)
        self.instance_tag = 'problems'

    def validate(self):
        if not super(ProblemsForm, self).validate():
            return False
        return True
