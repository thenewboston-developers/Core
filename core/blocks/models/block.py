import logging

from django.db import models

from core.core.constants import ACCOUNT_NUMBER_LENGTH, SIGNATURE_LENGTH
from core.core.models import CustomModel
from core.core.validators import HexStringValidator

logger = logging.getLogger(__name__)


class Block(CustomModel):
    id = models.UUIDField(primary_key=True)  # noqa: A003
    sender = models.CharField(
        max_length=ACCOUNT_NUMBER_LENGTH, validators=(HexStringValidator(ACCOUNT_NUMBER_LENGTH),)
    )
    signature = models.CharField(max_length=SIGNATURE_LENGTH, validators=(HexStringValidator(SIGNATURE_LENGTH),))
    recipient = models.CharField(
        max_length=ACCOUNT_NUMBER_LENGTH, validators=(HexStringValidator(ACCOUNT_NUMBER_LENGTH),)
    )
    amount = models.PositiveBigIntegerField()
    transaction_fee = models.PositiveBigIntegerField()
    payload = models.JSONField(null=True)

    def __str__(self):
        return f'{self.id} | {self.sender} -> {self.recipient} | {self.amount}'

    def save(self, *args, **kwargs):
        if not self._state.adding:
            # TODO(dmu) CRITICAL: Prohibit block update
            #                     https://github.com/thenewboston-developers/Core/issues/89
            logger.warning('Block update is not allowed')

        return super().save(*args, **kwargs)
