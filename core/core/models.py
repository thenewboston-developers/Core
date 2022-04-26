from django.db import models

from .managers import CustomManager


class CustomModel(models.Model):

    objects = CustomManager()

    class Meta:
        abstract = True
