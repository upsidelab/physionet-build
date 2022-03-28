from django.db.models import Manager


class WorkflowManager(Manager):
    def in_progress(self):
        return self.filter(status=self.model.INPROGRESS)
