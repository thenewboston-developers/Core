from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from core.core.constants import ACCOUNT_NUMBER_LENGTH
from core.core.models import CustomModel
from core.core.validators import HexStringValidator


def get_value(name):
    obj = Config.objects.get()
    return getattr(obj, name, None)


class Config(CustomModel):
    owner = models.CharField(
        max_length=ACCOUNT_NUMBER_LENGTH,
        validators=(HexStringValidator(ACCOUNT_NUMBER_LENGTH),),
        null=True,
        blank=True,
    )
    transaction_fee = models.PositiveBigIntegerField(validators=(MinValueValidator(1),), default=1)

    def __str__(self):
        return ', '.join(
            f'{field.name} = {getattr(self, field.name)}' for field in self._meta.get_fields() if field.name != 'id'
        )

    def save(self, *args, **kwargs):
        if Config.objects.count():
            raise ValidationError('Only one config instance is allowed')

        return super().save(*args, **kwargs)
