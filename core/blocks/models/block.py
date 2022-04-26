from django.db import models

from core.accounts.constants import ACCOUNT_NUMBER_LENGTH
from core.core.models import CustomModel


class Block(CustomModel):
    sender = models.CharField(max_length=ACCOUNT_NUMBER_LENGTH)
    recipient = models.CharField(max_length=ACCOUNT_NUMBER_LENGTH)
    amount = models.PositiveBigIntegerField(blank=True, null=True)
    payload = models.JSONField(null=True)

    def __str__(self):
        return f'{self.id} | {self.sender} -> {self.recipient} | {self.amount}'
