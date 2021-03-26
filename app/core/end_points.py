from flask import render_template, session, request
from ..src.utils.response import Response
from . import main


@main.route('/device', methods=["POST"])
def initiate():
    device_config = request.get_json()
    from .. import app_manager
    response = app_manager.register_device(device_config)
    return response.to_json()


@main.route('/end', methods=["POST"])
def end():
    data = request.get_json()
    _type = data.get("type", None)
    target_id = data.get("target_id", None)
    from .. import app_manager
    if _type == "device":
        response = app_manager.end_device(target_id)
    elif _type == "task":
        response = app_manager.end_task(target_id)
    elif _type == "all":
        response = app_manager.end()
    else:
        e = TypeError("Invalid type to end: {}".format(_type if _type is not None else "not given"))
        response = Response(False, None, e)
    return response.to_json()


@main.route('/ping')
def ping():
    from .. import app_manager
    response = app_manager.ping()
    return response.to_json()


@main.route('/command', methods=["POST"])
def command():
    from .. import app_manager
    data: dict = request.get_json()
    response = app_manager.command(data)
    return response.to_json()


@main.route('/task', methods=["POST"])
def task():
    from .. import app_manager
    data: dict = request.get_json()
    response = app_manager.register_task(data)
    return response.to_json()


@main.route('/data', methods=["GET"])
def get_data():
    from .. import app_manager
    args = dict(request.args)
    response = app_manager.get_data(args)
    return response.to_json()


@main.route('/data/latest', methods=['GET'])
def get_latest_data():
    from .. import app_manager
    args = dict(request.args)
    response = app_manager.get_latest_data(args)
    return response.to_json()


# @core.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user = User(username=form.name.data)
#             db.session.add(user)
#             db.session.commit()
#             session['known'] = False
#             if current_app.config['FLASKY_ADMIN']:
#                 send_email(current_app.config['FLASKY_ADMIN'], 'New User',
#                            'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         return redirect(url_for('.index'))
#     return render_template('index.html',
#                            form=form, name=session.get('name'),
#                            known=session.get('known', False))
