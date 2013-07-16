from sqlalchemy import Column, String, Text, Enum


class FeedbackMixin(object):
    feedback_email = Column(String(50))
    feedback_tag = Column(Enum('interest',
                               'problem',
                               'comment',
                               default='comment',
                               name='feedback_tag',
                               native_enum=False))
    feedback_priority = Column(Enum('low',
                                    'medium',
                                    'high',
                                    'urgent',
                                    default='low',
                                    name='requested_priority',
                                    native_enum=False))
    feedback_content = Column(Text)
