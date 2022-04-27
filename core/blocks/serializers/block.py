from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from core.accounts.models.account import Account
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
        if amount == 0:  # no need to update balances or create recipient account if there is no coin transfer
            return block

        # It is crucial to make select_for_update()
        sender_account = Account.objects.select_for_update().get_or_none(account_number=block.sender)

        # Just assert here, because it must have been validated in validate()
        assert sender_account
        assert sender_account.balance >= amount

        sender_account.balance -= amount
        sender_account.save()

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
        assert amount >= 0
        if amount == 0:  # no need for remaining validations since we are not sending coins
            return attrs

        # It is crucial to make select_for_update(), so we get database row lock till the moment of actual update
        sender_account = Account.objects.select_for_update().get_or_none(account_number=sender)
        if sender_account is None:
            raise ValidationError({'sender': ['Sender account does not exist']})

        if sender_account.balance < attrs['amount']:
            raise ValidationError({'amount': ['Amount is greater than sender account balance']})

        return attrs
