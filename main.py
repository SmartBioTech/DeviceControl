import os
from flask_migrate import Migrate
from app import create_app, db, setup_app_manager
from app.models import Device, Variable, Event, EventType, Value, Experiment

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
setup_app_manager(app)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
