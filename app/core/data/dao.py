import configparser
from flask_sqlalchemy import SQLAlchemy


class Dao:
    def __init__(self):
        self.db = None

    def setup_db(self, app, testing):
        config = self.load_db_config(testing)
        url = 'mysql://{}:{}@{}/{}'.format(config['user'], config['password'], config['host'], config['database'])
        app.config['SQLALCHEMY_DATABASE_URI'] = url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(app)
        self.db.create_all()

    @staticmethod
    def load_db_config(testing):
        config = configparser.ConfigParser()
        config.read('setup/config.ini')
        if not testing:
            return dict(config['PRODUCTION'])
        return dict(config['TESTING'])

    def insert(self, item):
        self.db.session.add(item)
        self.db.session.commit()


Dao = Dao()
