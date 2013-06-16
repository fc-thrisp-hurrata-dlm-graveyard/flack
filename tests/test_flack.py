from __future__ import with_statement
import sys
import os
from flask import Flask, render_template, current_app, g, request, redirect
from flask.ext.flack import (Flack, SQLAlchemyFeedbackDatastore,
        MongoEngineFeedbackDatastore, PeeweeFeedbackDatastore, FeedbackMixin)
from flask.ext.sqlalchemy import SQLAlchemy
import unittest

def make_app(**kwargs):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db = SQLAlchemy(app)
    @app.before_first_request
    def before_first_request():
        db.drop_all()
        db.create_all()
    class TestFeedback(db.Model, FeedbackMixin):
        id = db.Column(db.Integer(), primary_key=True)
    return app, db, TestFeedback

class FlackBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.flack_app, self.db, TestFeedback = make_app()
        self.datastore = SQLAlchemyFeedbackDatastore(self.db, TestFeedback)
        Flack(self.flack_app, self.datastore)

    def tearDown(self):
        self.flack_app = None

    def test_initialize(self):
        self.assertIsNotNone(self.flack_app.extensions['flack'])

class TestFlack(FlackBaseTestCase):
    pass

if __name__ == '__main__':
    unittest.main()
