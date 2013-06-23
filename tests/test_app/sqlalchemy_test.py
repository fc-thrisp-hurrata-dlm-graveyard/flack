import sys
import os

sys.path.pop(0)
sys.path.insert(0, os.getcwd())


from flask.ext.sqlalchemy import SQLAlchemy
from flask_flack import Flack, FeedbackMixin, SQLAlchemyFeedbackDatastore
from tests.test_app import create_app as create_base_app


def create_app(config, **kwargs):

    app = create_base_app(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db = SQLAlchemy(app)

    class TestFeedback(db.Model, FeedbackMixin):
        id = db.Column(db.Integer(), primary_key=True)

    @app.before_first_request
    def before_first_request():
        db.drop_all()
        db.create_all()

    test_datastore = SQLAlchemyFeedbackDatastore(db, TestFeedback)

    app.flack_e = Flack(app, datastore=test_datastore, **kwargs)
    app.hold_database = db
    app.FEEDBACK_MODEL = TestFeedback

    return app

if __name__ == '__main__':
    create_app({}).run()
