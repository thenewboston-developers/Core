from django.db import models

from ..constants import ACCOUNT_NUMBER_LENGTH


class Account(models.Model):
    account_number = models.CharField(max_length=ACCOUNT_NUMBER_LENGTH, primary_key=True)
    balance = models.PositiveBigIntegerField()

    def __str__(self):
        return f'{self.account_number} | {self.balance}'
