import inspect
import urlparse
import flask_wtf as wtf
from flask import request, current_app
from flask_wtf import Form as BaseForm, TextField, TextAreaField, SelectField,\
    SubmitField, HiddenField, BooleanField, ValidationError, Field
from werkzeug import LocalProxy
from .utils import get_message


_datastore = LocalProxy(lambda: current_app.extensions['flack'].datastore)

_default_choices = [('low', 'low'),
                    ('medium', 'medium'),
                    ('high', 'high'),
                    ('urgent', 'urgent')]

_default_form_field_labels = {
        'email': 'Email Address',
        'interest': 'Interest',
        'submit_interest': 'Submit',
        'problem': 'Problem',
        'requested_priority': 'priority',
        'submit_problem': 'Tell us your problem',
        'comment': 'Comment',
        'submit_comment': 'Tell us what you think'
        }

def get_form_field_label(key):
     return _default_form_field_labels.get(key, '')


class ValidatorMixin(object):
    def __call__(self, form, field):
        if self.message and self.message.isupper():
            self.message = get_message(self.message)[0]
        return super(ValidatorMixin, self).__call__(form, field)


class Required(ValidatorMixin, wtf.Required):
    pass


class Email(ValidatorMixin, wtf.Email):
    pass


email_required = Required(message='EMAIL_NOT_PROVIDED')
email_validator = Email(message='INVALID_EMAIL_ADDRESS')


class Form(BaseForm):
    def __init__(self, *args, **kwargs):
        if current_app.testing:
            self.TIME_LIMIT = None
        super(Form, self).__init__(*args, **kwargs)


class EmailFormMixin():
    email = TextField(get_form_field_label('email'),
        validators=[email_required,
                    email_validator])


class TagMixin():
    feedback_tag = HiddenField("feedback_tag")


class NextFormMixin():
    next = HiddenField()

    def validate_next(self, field):
        url_next = urlparse.urlsplit(field.data)
        url_base = urlparse.urlsplit(request.host_url)
        if url_next.netloc and url_next.netloc != url_base.netloc:
            field.data = ''
            raise ValidationError(get_message('INVALID_REDIRECT')[0])


class InterestForm(Form, TagMixin, EmailFormMixin, NextFormMixin):
    interest = TextAreaField(get_form_field_label('interest'))
    submit = SubmitField(get_form_field_label('submit_interest'))

    def validate(self):
        if not super(InterestForm, self).validate():
            return False
        return True


class ProblemForm(Form, TagMixin, EmailFormMixin, NextFormMixin):
    requested_priority = SelectField(get_form_field_label('requested_priority'), choices=_default_choices)
    problem = TextAreaField(get_form_field_label('problem'))
    submit = SubmitField(get_form_field_label('submit_problem'))

    def validate(self):
        if not super(ProblemForm, self).validate():
            return False
        return True


class CommentForm(Form, TagMixin, EmailFormMixin, NextFormMixin):
    comment = TextAreaField(get_form_field_label('comment'))
    submit = SubmitField(get_form_field_label('submit_comment'))

    def validate(self):
        if not super(CommentForm, self).validate():
            return False
        return True
