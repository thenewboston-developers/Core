from django.db import models

from ..constants import ACCOUNT_NUMBER_LENGTH, DISPLAY_NAME_MAX_LENGTH


class Account(models.Model):
    account_number = models.CharField(max_length=ACCOUNT_NUMBER_LENGTH, primary_key=True)
    avatar = models.URLField(blank=True)
    balance = models.PositiveBigIntegerField()
    display_name = models.CharField(blank=True, max_length=DISPLAY_NAME_MAX_LENGTH)

    def __str__(self):
        return f'{self.account_number} | {self.balance}'
