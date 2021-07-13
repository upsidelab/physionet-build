from abc import ABCMeta

from django.db import models


class AbstractModelMeta(ABCMeta, type(models.Model)):
    pass


class ABCModel(models.Model, metaclass=AbstractModelMeta):
    """
    Like Python ABC, except compatible with Django models.
    Used to enable the use of abstract methods in model subclasses.

    https://gist.github.com/gavinwahl/7778717

    """

    class Meta:
        abstract = True
