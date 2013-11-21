from __future__ import with_statement
from tests import *


class FeedbackTest(FlackTest): pass


class FeedbackModelMixinTests(FlackTest):
    def test_feedback_mixedin(self): pass
    #    for x in (self.a_problem,
    #              self.an_interest,
    #              self.a_suggestion,
    #              self.a_suggestion2):
    #        self.assertIsNotNone(x)
    #    self.assertEqual(self.a_suggestion.feedback_content,
    #                     self.a_suggestion2.feedback_content)


class FeedbackDataStoreTests(FlackTest):
    def test_unimplemented(self): pass
        #self.assertRaises(NotImplementedError, self.base_ds.put, None)
        #self.assertRaises(NotImplementedError, self.base_ds.delete, None)

    def test_create_feedback(self): pass
        #self.app.hold_database.create_all()
        #fb = self._ds.create_feedback(feedback_tag='problem',
        #                              feedback_email='test@test.com',
        #                              feedback_priority='urgent',
        #                              feedback_content='I have a problem')
        #self._ds.commit()
        #self.assertIsNotNone(fb)
        #self.assertEqual(fb.feedback_tag, 'problem')
        #self.assertEqual(fb.feedback_email, 'test@test.com')
        #self.assertEqual(fb.feedback_priority, 'urgent')
        #self.assertEqual(fb.feedback_content, 'I have a problem')
        #fetched = self.app.FEEDBACK_MODEL.query.get(1)
        #self.assertEqual(fb, fetched)
        #self.assertEqual(fb.feedback_tag, fetched.feedback_tag)


class ViewTests(FeedbackTest):
    def test_get_feedback_form(self): pass
    #    for fb in ('comment', 'problem', 'interest'):
    #        r = self._get('/feedback/{}'.format(fb))
    #        self.assertIsNotNone(r.data)

    def test_post_feedback_form(self): pass
    #    data = dict(feedback_tag='problem',
    #                feedback_email='test@test.com',
    #                feedback_priority='urgent',
    #                feedback_content='I have a problem',)
    #    r = self._post('/feedback', data=data)
    #    #self.assert_flashes('hello')
    #    self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    unittest.main()
