import channels.layers
from asgiref.sync import async_to_sync
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

from core.blocks.consumers import BlockConsumer

from ..models.block import Block
from ..serializers.block import BlockSerializer


def send(block_data):
    channel_layer = channels.layers.get_channel_layer()
    payload = {'type': 'send.block', 'message': block_data}
    async_to_sync(channel_layer.group_send)(BlockConsumer.group_name(block_data['recipient']), payload)


class BlockViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    # TODO(dmu) MEDIUM: Why do we need `filterset_fields` given that `filter_backends` is not set?
    filterset_fields = ('amount', 'recipient', 'sender')
    queryset = Block.objects.order_by('id').all()
    serializer_class = BlockSerializer

    def perform_create(self, serializer):
        rv = super().perform_create(serializer)
        send(serializer.data)
        return rv
