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

    def validate(self, attrs):
        attrs = super().validate(attrs)

        sender = attrs['sender']
        if sender == attrs['recipient']:
            raise ValidationError('Sender and recipient can not be the same')

        if not is_dict_signature_valid(attrs, attrs['sender'], attrs['signature']):
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
