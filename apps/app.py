from flask import Flask

from apps.config import config


def create_app(config_key):
    # Flaskインスタンスの作成
    app = Flask(__name__)

    app.config.from_object(config[config_key])

    from apps.generator import views as gen_views
    app.register_blueprint(gen_views.gen)
    return app