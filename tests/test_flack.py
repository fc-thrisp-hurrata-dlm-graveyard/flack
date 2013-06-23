from __future__ import with_statement
import hmac
from hashlib import sha1
import unittest
from flask import session
from test_app.sqlalchemy_test import create_app
from flask_flack.datastore import Datastore

class FeedbackTest(unittest.TestCase):

    APP_KWARGS = {}
    FEEDBACK_CONFIG = None

    def setUp(self):
        super(FeedbackTest, self).setUp()

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




class FeedbackModelMixinTests(FeedbackTest):

    def setUp(self):
        super(FeedbackModelMixinTests, self).setUp()
        f = self.app.FEEDBACK_MODEL
        self.a_problem = f(feedback_tag='problem',
                           feedback_priority='medium',
                           feedback_content="I have a problem")
        self.an_interest = f(feedback_tag='interest',
                             feedback_content="I am interested")
        self.a_suggestion = f(feedback_tag='comment',
                              feedback_content="I have a suggestion")
        self.a_suggestion2 = f(feedback_tag='comment',
                               feedback_content="I have a suggestion")

    def test_feedback_mixedin(self):
        for x in (self.a_problem,
                  self.an_interest,
                  self.a_suggestion,
                  self.a_suggestion2):
            self.assertIsNotNone(x)
        self.assertEqual(self.a_suggestion.feedback_content,
                         self.a_suggestion2.feedback_content)


class DataStoreTests(FeedbackTest):

    def setUp(self):
        super(DataStoreTests, self).setUp()
        self.base_ds = Datastore(None)
        self._ds = self.app.extensions['flack'].datastore

    def test_unimplemented(self):
        self.assertRaises(NotImplementedError, self.base_ds.put, None)
        self.assertRaises(NotImplementedError, self.base_ds.delete, None)

    def test_create_feedback(self):
        self.app.hold_database.create_all()
        fb = self._ds.create_feedback(feedback_tag='problem',
                                      feedback_email='test@test.com',
                                      feedback_priority='urgent',
                                      feedback_content='I have a problem')
        self._ds.commit()
        self.assertIsNotNone(fb)
        self.assertEqual(fb.feedback_tag, 'problem')
        self.assertEqual(fb.feedback_email, 'test@test.com')
        self.assertEqual(fb.feedback_priority, 'urgent')
        self.assertEqual(fb.feedback_content, 'I have a problem')
        fetched = self.app.FEEDBACK_MODEL.query.get(1)
        self.assertEqual(fb, fetched)
        self.assertEqual(fb.feedback_tag, fetched.feedback_tag)


class ViewTests(FeedbackTest):

    def test_get_feedback_form(self):
        for fb in ('comment', 'problem', 'interest'):
            r = self._get('/feedback/{}'.format(fb))
            self.assertIsNotNone(r.data)

    def test_post_feedback_form(self):
        data = dict(feedback_tag='problem',
                    feedback_email='test@test.com',
                    feedback_priority='urgent',
                    feedback_content='I have a problem',)
        r = self._post('/feedback', data=data)
        #self.assert_flashes('hello')
        self.assertEqual(r.status_code, 200)

if __name__ == '__main__':
    unittest.main()
