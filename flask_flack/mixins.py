from sqlalchemy import Column, String, Text, Enum


class FeedbackMixin(object):
    feedback_tag = Column(String(50), default='feedback')
    feedback_email = Column(String(50))
    feedback_priority = Column(String(50))
    feedback_content = Column(Text)
