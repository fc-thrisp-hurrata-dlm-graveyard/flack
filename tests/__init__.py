from flask_flack import *
import hmac
from hashlib import sha1
import unittest
from flask import session
from test_app.sqlalchemy_test import create_app
from flask_flack.datastore import Datastore

"""
    def setUp(self):
        super(FeedbackModelMixinTests, self).setUp()
        f = self.app.FEEDBACK_MODEL
        self.problem_1 = f(feedback_tag='problem',
                           feedback_priority='medium',
                           feedback_content="I have a problem")
        self.interest_1 = f(feedback_tag='interest',
                             feedback_content="I am interested")
        self.comment_1 = f(feedback_tag='comment',
                              feedback_content="I have a suggestion")
        self.comment_2 = f(feedback_tag='comment',
                               feedback_content="I have a suggestion")
"""
"""
    def setUp(self):
        super(DataStoreTests, self).setUp()
        self.base_ds = Datastore(None)
        self._ds = self.app.extensions['feedback'].datastore
"""

class FlackTest(unittest.TestCase):
    APP_KWARGS = {}
    FEEDBACK_CONFIG = None

    def setUp(self):
        app_kwargs = self.APP_KWARGS
        app = self._create_app(self.FEEDBACK_CONFIG or {}, **app_kwargs)
        app.debug = False
        app.config['TESTING'] = True

        self.app = app
        self.client = app.test_client()

        with self.client.session_transaction() as session:
            session['csrf'] = 'csrf_token'

        csrf_hmac = hmac.new(self.app.config['SECRET_KEY'],
                             'csrf_token'.encode('utf8'), digestmod=sha1)
        self.csrf_token = '##' + csrf_hmac.hexdigest()

    def tearDown(self):
        self.app = None

    def _create_app(self, feedback_config, **kwargs):
        return create_app(feedback_config, **kwargs)

    def _get(self,
             route,
             content_type=None,
             follow_redirects=None,
             headers=None):
        return self.client.get(route,
                               follow_redirects=follow_redirects,
                               content_type=content_type or 'text/html',
                               headers=headers)

    def _post(self,
              route,
              data=None,
              content_type=None,
              follow_redirects=True,
              headers=None):
        if isinstance(data, dict):
            data['csrf_token'] = self.csrf_token

        return self.client.post(route,
                                data=data,
                                follow_redirects=follow_redirects,
                                content_type=content_type or
                                'application/x-www-form-urlencoded',
                                headers=headers)

    def assert_flashes(self, expected_message, expected_category='message'):
        with self.client.session_transaction() as session:
            try:
                category, message = session['_flashes'][0]
            except KeyError:
                raise AssertionError('nothing flashed')
            assert expected_message in message
            assert expected_category == category
