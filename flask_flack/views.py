from flask import (current_app, redirect, request, render_template, jsonify,
                   after_this_request, Blueprint)
from werkzeug import LocalProxy
from werkzeug.datastructures import MultiDict
from .utils import get_url, get_post_feedback_redirect, get_message, do_flash

_flack = LocalProxy(lambda: current_app.extensions['flack'])
_datastore = LocalProxy(lambda: _flack.datastore)


def _render_json(form):
    has_errors = len(form.errors) > 0

    if has_errors:
        code = 400
        response = dict(errors=form.errors)
    else:
        code = 200
        response = dict(result='ok')

    return jsonify(dict(meta=dict(code=code), response=response))


def _commit(response=None):
    _datastore.commit()
    return response


def _ctx(endpoint):
    return _flack._run_ctx_processor(endpoint)


def get_form_class(which_form):
    wf = "{}_form".format(which_form)
    return getattr(_flack, wf)


def get_relevant_form():
    requested_form = request.endpoint.rsplit('.')[-1]
    form_class = get_form_class(requested_form)
    form = form_class(feedback_tag=requested_form)

    form.next.data = get_url(request.args.get('next')) \
        or get_url(request.form.get('next')) or ''

    return render_template('feedback/{}.html'.format(requested_form),
                           form=form,
                           **_ctx(requested_form))


def feedback():
    requested_form = request.form['feedback_tag']

    form_class = get_form_class(requested_form)

    if request.json:
        form_data = MultiDict(request.json)
    else:
        form_data = request.form

    form = form_class(form_data)

    if form.validate_on_submit():
        _datastore.create_feedback(**form.to_dict())
        after_this_request(_commit)

        if request.json:
            return _render_json(form)
        else:
            do_flash(*get_message("{}_RESPOND".format(requested_form.upper())))
            return redirect(get_post_feedback_redirect())

    return render_template('feedback/{}.html'.format(requested_form),
                           form=form,
                           **_ctx(requested_form))


def create_blueprint(state, import_name):
    bp = Blueprint(state.blueprint_name, import_name,
                   url_prefix=state.url_prefix,
                   subdomain=state.subdomain,
                   template_folder='templates')
    bp.route(state.interest_url,
             methods=['GET'],
             endpoint='interest')(get_relevant_form)
    bp.route(state.problem_url,
             methods=['GET'],
             endpoint='problem')(get_relevant_form)
    bp.route(state.comment_url,
             methods=['GET'],
             endpoint='comment')(get_relevant_form)
    bp.route(state.feedback_url,
             methods=['POST'],
             endpoint='feedback')(feedback)
    return bp
