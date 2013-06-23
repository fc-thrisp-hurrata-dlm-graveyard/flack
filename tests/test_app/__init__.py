from flask import Flask, render_template, current_app
from werkzeug.local import LocalProxy

ds = LocalProxy(lambda: current_app.extensions['security'].datastore)


def create_app(config):
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'secret'
    app.config['TESTING'] = True

    for key, value in config.items():
        app.config[key] = value

    @app.route('/')
    def index():
        return render_template('index.html', content='Home Page')

    return app
