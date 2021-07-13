from abc import ABCMeta

from django.db import models


class AbstractModelMeta(ABCMeta, type(models.Model)):
    """
    Like Python ABCMeta, except compatible with Django models.
    Used to enable the use of abstract methods in model subclasses.

    Ref: https://gist.github.com/gavinwahl/7778717

    See below for how to use.
    """
    pass


"""
class ABCModel(models.Model, metaclass=AbstractModelMeta):
    class Meta:
        abstract = True

    @abstractmethod
    def methodtobeimplemented(self):
        pass


class ActualModel(ABCModel):
    def methodtobeimplemented(self):
        somelogic()

"""

