from sqlalchemy import Column, Integer, String, Text, Enum

class FeedbackMixin(object):
    feedback_tag = Column(Enum('interest', 'problem', 'comment'), default='comment')
    requested_priority = Column(Enum('low','medium', 'high', 'urgent', 'immediate'), default='low')
    assigned_priority = Column(Enum('low','medium', 'high', 'urgent', 'immediate'), default='low')
    content = Column(Text)
