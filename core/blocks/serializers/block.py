from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from core.accounts.models.account import Account
from core.config.models import get_value
from core.core.serializers import ValidateFieldsMixin
from core.core.utils.cryptography import is_dict_signature_valid

from ..models.block import Block


class BlockSerializer(ValidateFieldsMixin, ModelSerializer):

    class Meta:
        model = Block
        fields = '__all__'

    def create(self, validated_data):
        # TODO(dmu) MEDIUM: Consider moving the logic to core.blocks.views.block.BlockViewSet.perform_create()
        #                   Another option is to move it Django signal handler
        block = super().create(validated_data)

        amount = block.amount
        assert amount >= 0

        transaction_fee = get_value('transaction_fee')
        assert transaction_fee > 0

        total_amount = amount + transaction_fee
        assert total_amount > 0

        # It is crucial to make select_for_update()
        sender_account = Account.objects.select_for_update().get_or_none(account_number=block.sender)

        # Just assert here, because it must have been validated in validate()
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

        return block

    def validate(self, attrs):
        attrs = super().validate(attrs)

        sender = attrs['sender']
        if sender == attrs['recipient']:
            raise ValidationError('Sender and recipient can not be the same')

        if not is_dict_signature_valid(attrs, attrs['sender']):
            raise ValidationError({'signature': ['Invalid']})

        amount = attrs['amount']
        total_amount = amount + get_value('transaction_fee')
        assert total_amount > 0

        # It is crucial to make select_for_update(), so we get database row lock till the moment of actual update
        sender_account = Account.objects.select_for_update().get_or_none(account_number=sender)
        if sender_account is None:
            raise ValidationError({'sender': ['Sender account does not exist']})

        if sender_account.balance < total_amount:
            raise ValidationError({'amount': ['Total amount is greater than sender account balance']})

        return attrs

    @staticmethod
    def validate_transaction_fee(value):
        min_transaction_fee = get_value('transaction_fee')
        if value < min_transaction_fee:
            raise ValidationError('Too small amount')

        return value
