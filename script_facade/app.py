from flask import Flask

from script_facade import api


def create_app(testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('script_facade')
    app.config.from_object('script_facade.client.config')
    register_blueprints(app)

    return app

def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(api.fhir.blueprint)
