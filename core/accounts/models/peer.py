from django.db import models

from core.core.models import CustomModel


class Peer(CustomModel):
    allowing_peer = models.ForeignKey('Account', related_name='allowing_peer', on_delete=models.CASCADE)
    allowed_peer = models.ForeignKey('Account', related_name='allowed_peer', on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('allowing_peer', 'allowed_peer'), name='unique_peer_relation')]
