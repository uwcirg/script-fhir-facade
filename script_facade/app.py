from flask import Flask
import redis
import requests_cache

from script_facade import api


def create_app(testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('script_facade')
    app.config.from_object('script_facade.client.config')
    register_blueprints(app)
    configure_app(app)
    configure_cache(app)

    return app


def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(api.fhir.blueprint)
    app.register_blueprint(api.misc.blueprint)


def configure_app(app):
    """Load successive configs - overriding defaults"""

    app.config.from_object('script_facade.config')


def configure_cache(app):
    """Configure caching libraries"""

    # NB this effectively turns caching on for ALL requests API calls.
    # To temporarily disable, wrap w/ context manager:
    #
    #   with requests_cache.disabled():
    #     requests.get('http://httpbin.org/get')
    app.logger.info(
        f"Initiating requests.cache with {app.config.get('REQUEST_CACHE_URL')}")
    requests_cache.install_cache(
        cache_name=app.name,
        backend='redis',
        expire_after=app.config['REQUEST_CACHE_EXPIRE'],
        include_get_headers=True,
        old_data_on_error=True,
        connection=redis.StrictRedis.from_url(app.config.get("REQUEST_CACHE_URL")),
    )
