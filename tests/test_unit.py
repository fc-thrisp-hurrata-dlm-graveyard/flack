from tests import *


class FeedbackModelMixinTests(FlackTest):
    def test_feedback_mixedin(self): pass


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


