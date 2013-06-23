class Datastore(object):
    def __init__(self, db):
        self.db = db

    def commit(self):
        pass

    def put(self, model):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError


class SQLAlchemyDatastore(Datastore):
    def commit(self):
        self.db.session.commit()

    def put(self, model):
        self.db.session.add(model)
        return model

    def delete(self, model):
        self.db.session.delete(model)


class MongoEngineDatastore(Datastore):
    def put(self, model):
        model.save()
        return model

    def delete(self, model):
        model.delete()


class PeeweeDatastore(Datastore):
    def put(self, model):
        model.save()
        return model

    def delete(self, model):
        model.delete_instance()


class FeedbackDatastore(object):
    def __init__(self, feedback_model):
        self.feedback_model = feedback_model

    #def _prepare_create_feedback_args(self, **kwargs):
        #return kwargs#return {k: v for k,v in kwargs.items() if k in feedback_model.__dict__.keys()}

    def create_feedback(self, **kwargs):
        """Creates and returns new feedback from the given parameters."""
        feedback = self.feedback_model(**kwargs)
        return self.put(feedback)


class SQLAlchemyFeedbackDatastore(SQLAlchemyDatastore, FeedbackDatastore):
    def __init__(self, db, feedback_model):
        SQLAlchemyDatastore.__init__(self, db)
        FeedbackDatastore.__init__(self, feedback_model)

    def find_feedback(self, feedback_tag):
        pass


class MongoEngineFeedbackDatastore(MongoEngineDatastore, FeedbackDatastore):
    def __init__(self, db, feedback_model):
        MongoEngineDatastore.__init__(self, db)
        FeedbackDatastore.__init__(self, feedback_model)

    def find_feedback(self, feedback_tag):
        pass


class PeeweeFeedbackDatastore(PeeweeDatastore, FeedbackDatastore):
    def __init__(self, db, feedback_model):
        PeeweeDatastore.__init__(self, db)
        FeedbackDatastore.__init__(self, feedback_model)

    def find_feedback(self, feedback_tag):
        pass
