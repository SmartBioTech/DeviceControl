import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard to guess string')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
                   ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_USERNAME = os.environ.get('USERNAME')
    DB_PASSWORD = os.environ.get('PASSWORD')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    FLASK_DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/device_control_devel'.format(Config.DB_USERNAME,
                                                                                    Config.DB_PASSWORD)


class TestingConfig(Config):
    FLASK_DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/device_control_test'.format(Config.DB_USERNAME,
                                                                                   Config.DB_PASSWORD)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/device_control'.format(Config.DB_USERNAME,
                                                                              Config.DB_PASSWORD)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
