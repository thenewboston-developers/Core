from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from core.accounts.models.account import Account

from ..models.block import Block


class BlockSerializer(ModelSerializer):

    class Meta:
        model = Block
        fields = '__all__'


class BlockSerializerCreate(ModelSerializer):

    class Meta:
        model = Block
        fields = '__all__'

    def create(self, validated_data):
        # TODO(dmu) MEDIUM: Consider moving the logic to core.blocks.views.block.BlockViewSet
        block = super().create(validated_data)

        # TODO(dmu) MEDIUM: It looks more consistent to let amount be 0, but not None
        amount = block.amount
        if amount is None:
            return block

        # This more consistent than validating in separate method, because of setting a database lock on the row
        sender_account = Account.objects.select_for_update().get_or_none(account_number=block.sender)
        if sender_account is None:
            raise ValidationError({'sender': ['Sender account does not exist']})

        if sender_account.balance < amount:
            raise ValidationError({'amount': ['Amount is greater than sender account balance']})

        sender_account.balance -= amount
        sender_account.save()

        recipient_account, is_created = Account.objects.select_for_update().get_or_create(
            account_number=block.recipient, defaults={'balance': amount}
        )

        if not is_created:
            recipient_account.balance += amount
            recipient_account.save()

        return block

    def update(self, instance, validated_data):
        # TODO(dmu) HIGH: Introduce a better way of disabling block update
        #                 https://github.com/thenewboston-developers/Core/issues/24
        raise RuntimeError('Method unavailable')

    def validate(self, data):
        data = super(BlockSerializerCreate, self).validate(data)

        if data['sender'] == data['recipient']:
            raise ValidationError('Sender and recipient can not be the same')

        return data

    @staticmethod
    def validate_amount(amount):
        # TODO(dmu) MEDIUM: Instead of this validation use min_value=1 on model level or minimum value validator
        if amount <= 0:
            raise ValidationError('Amount must be greater than 0')

        return amount
