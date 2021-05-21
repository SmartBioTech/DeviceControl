import os
import click
from flask_migrate import Migrate
from app import create_app, db, setup_app_manager
from app.models import Device, Variable, Event, EventType, Value, Experiment, Log

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
setup_app_manager(app)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names != ('', ):
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def profile():
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app)
    app.run()
