from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from .main.app_manager import AppManager

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
app_manager = AppManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    app_context = app.app_context()
    app_context.push()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    app_manager.init_app()

    app_context = app.app_context()
    app_context.push()
    db.create_all()

    return app
