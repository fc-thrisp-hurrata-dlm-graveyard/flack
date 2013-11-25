from tests import *


class DefaultFeedbackTest(FlackTest):
    def test_extension(self):
        self.assertIsNotNone(self.app.extensions['feedback'])
        self.assertEqual(self.app.flack._state, self.app.extensions['feedback'])
