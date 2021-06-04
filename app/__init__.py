from datetime import datetime, timedelta

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from .core.app_manager import AppManager
from flask_apscheduler import APScheduler

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy(session_options={'expire_on_commit': False})
scheduler = APScheduler()
app_manager = AppManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    db.app = app
    db.init_app(app)

    scheduler.init_app(app)
    scheduler.add_job(func=app_manager.restore_session, id='load_session',
                      run_date=datetime.now() + timedelta(seconds=30))
    scheduler.start()

    from .core import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


def setup_app_manager(app):
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    app_manager.init_app()
    app_manager.dataManager.store_permanent()
