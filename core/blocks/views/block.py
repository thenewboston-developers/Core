from functools import partial

from rest_framework.mixins import CreateModelMixin, ListModelMixin

from core.accounts import consumers
from core.accounts.consumers import MessageType
from core.accounts.models import Account
from core.config.models import get_value
from core.core.utils.misc import apply_on_commit
from core.core.views import CustomGenericViewSet

from ..models.block import Block
from ..serializers.block import BlockSerializer


class BlockViewSet(CreateModelMixin, ListModelMixin, CustomGenericViewSet):
    queryset = Block.objects.order_by('id').all()
    serializer_class = BlockSerializer

    def perform_create(self, serializer):
        rv = super().perform_create(serializer)
        message = serializer.data

        # TODO(dmu) MEDIUM: Consider moving apply_on_commit(consumers.send) to Block.save()
        # `consumers.send` so we can mock `send` in `consumers`
        apply_on_commit(partial(consumers.send, MessageType.CREATE_BLOCK, message['recipient'], message))

        block = serializer.instance
        amount = block.amount
        assert amount >= 0

        transaction_fee = get_value('transaction_fee')
        assert transaction_fee > 0

        total_amount = amount + transaction_fee
        assert total_amount > 0

        # It is crucial to make select_for_update()
        sender_account = Account.objects.select_for_update().get_or_none(account_number=block.sender)

        # Just assert here, because it must have been validated in serializer
        assert sender_account
        sender_account.balance -= total_amount
        assert sender_account.balance >= 0

        sender_account.save()

        if amount == 0:  # no need to update balances or create recipient account if there is no coin transfer
            return block

        recipient_account, is_created = Account.objects.select_for_update().get_or_create(
            account_number=block.recipient, defaults={'balance': amount}
        )

        if not is_created:
            recipient_account.balance += amount
            recipient_account.save()

        return rv
