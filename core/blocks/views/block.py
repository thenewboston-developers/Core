from rest_framework.mixins import CreateModelMixin, ListModelMixin

from core.accounts.consumers import MessageType, send
from core.core.views import CustomGenericViewSet

from ..models.block import Block
from ..serializers.block import BlockSerializer


class BlockViewSet(CreateModelMixin, ListModelMixin, CustomGenericViewSet):
    queryset = Block.objects.order_by('id').all()
    serializer_class = BlockSerializer

    def perform_create(self, serializer):
        rv = super().perform_create(serializer)
        message = serializer.data
        send(MessageType.CREATE_BLOCK, message['recipient'], message)
        return rv
