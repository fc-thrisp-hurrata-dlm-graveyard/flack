from flask import (current_app, redirect, request, render_template, jsonify,
                   after_this_request, Blueprint)
from werkzeug import LocalProxy
from .utils import (get_post_feedback_redirect, get_message, do_flash)


_feedback = LocalProxy(lambda: current_app.extensions['feedback'])

_datastore = LocalProxy(lambda: _feedback.datastore)

_endpoint = LocalProxy(lambda: request.endpoint.rsplit('.')[-1])


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


def feedback():
    use_form = _feedback.current_form()

    if use_form.validate_on_submit():
        _datastore.create_feedback(**use_form.to_dict())
        after_this_request(_commit)

        if request.json:
            return _render_json(form)
        else:
            do_flash(*get_message("{}_RESPOND".format(_endpoint.upper())))
            return redirect(get_post_feedback_redirect())

    return render_template(_feedback.current_template)


def create_blueprint(state, import_name):
    bp = Blueprint(state.blueprint_name,
                   import_name,
                   url_prefix=state.url_prefix,
                   subdomain=state.subdomain,
                   template_folder='templates')
    bp.route(state.feedback_url,
             methods=['GET', 'POST'],
             endpoint='feedback')(feedback)
    return bp
