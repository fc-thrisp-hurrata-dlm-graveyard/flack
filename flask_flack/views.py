from flask import current_app, redirect, request, render_template, jsonify, \
    after_this_request, Blueprint
from werkzeug import LocalProxy
from werkzeug.datastructures import MultiDict
from .utils import get_url, get_post_feedback_redirect

_flack = LocalProxy(lambda: current_app.extensions['flack'])

def _render_json(form):
    has_errors = len(form.errors) > 0

    if has_errors:
        code = 400
        response = dict(errors=form.errors)
    else:
        code = 200
        response = dict(user=dict(id=str(form.user.id)))

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
    requested = request.endpoint.rsplit('.')[-1]
    form_class = get_form_class(requested)

    if request.json:
        form = form_class(MultiDict(request.json))
    else:
        form = form_class(feedback_tag=requested)

    if request.json:
        return _render_json(form)

    form.next.data = get_url(request.args.get('next')) \
                     or get_url(request.form.get('next')) or ''

    return render_template('feedback/{}.html'.format(requested),
                           form=form,
                           **_ctx(requested))

def feedback():
    form_class = get_form_class(request.form['feedback_tag'])

    if request.json:
        form = form_class(MultiDict(request.json))
    else:
        form = form_class()

    #return str(form)
    return render_template('test_.html', f=form)

    #if form.validate_on_submit():
        #create feedback

    #    if not request.json:
    #        return redirect(get_post_feedback_redirect())


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
