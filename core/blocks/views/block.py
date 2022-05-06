from rest_framework.mixins import CreateModelMixin, ListModelMixin

from core.accounts.consumers import MessageType, send
from core.core.utils.misc import apply_on_commit
from core.core.views import CustomGenericViewSet

from ..models.block import Block
from ..serializers.block import BlockSerializer


class BlockViewSet(CreateModelMixin, ListModelMixin, CustomGenericViewSet):
    queryset = Block.objects.order_by('id').all()
    serializer_class = BlockSerializer

    def perform_create(self, serializer):
        rv = super().perform_create(serializer)
        # We assign `serializer.data` to `message` kwarg to avoid to avoid closure creation (please, keep it)
        apply_on_commit(lambda message=serializer.data: send(MessageType.CREATE_BLOCK, message['recipient'], message))
        return rv
