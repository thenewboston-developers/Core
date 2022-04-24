from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from core.accounts.models.account import Account

from ..models.block import Block


class BlockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Block
        fields = '__all__'


class BlockSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = Block
        fields = '__all__'

    def create(self, validated_data):
        # TODO(dmu) CRITICAL: Use `select for update` to update the balance
        #                     https://github.com/thenewboston-developers/Core/issues/24
        # TODO(dmu) HIGH: Use implementation more consistent with ModelSerializer
        #                 https://github.com/thenewboston-developers/Core/issues/24
        try:
            # TODO(dmu) HIGH: Use atomic requests instead of explicit transaction management with
            #                 transaction.atomic()
            #                 https://github.com/thenewboston-developers/Core/issues/24
            with transaction.atomic():
                block = Block.objects.create(**validated_data)
                amount = block.amount

                if amount is not None:
                    Account.objects.filter(account_number=block.sender).update(balance=F('balance') - amount)

                    recipient = Account.objects.filter(account_number=block.recipient).first()

                    if recipient:
                        recipient.balance += amount
                        recipient.save()
                    else:
                        Account.objects.create(account_number=block.recipient, balance=amount)
        except Exception as e:
            # TODO(dmu) HIGH: Avoid too broad exceptions
            #                 https://github.com/thenewboston-developers/Core/issues/24
            raise serializers.ValidationError(e)

        return block

    def update(self, instance, validated_data):
        # TODO(dmu) HIGH: Introduce a better way of disabling block update
        #                 https://github.com/thenewboston-developers/Core/issues/24
        raise RuntimeError('Method unavailable')

    def validate(self, data):
        data = super(BlockSerializerCreate, self).validate(data)
        sender = data['sender']
        recipient = data['recipient']
        amount = data.get('amount')

        if sender == recipient:
            raise serializers.ValidationError('Sender and recipient can not be the same')

        if amount is not None:
            # TODO(dmu) LOW: Handle the case of not existing sender account (there may be a database change
            #                between validation and getting the account)
            #                https://github.com/thenewboston-developers/Core/issues/24
            sender_account = Account.objects.filter(account_number=sender).first()

            if amount > sender_account.balance:
                raise serializers.ValidationError('Amount is greater than senders account balance')

        return data

    @staticmethod
    def validate_amount(amount):
        if amount == 0:
            raise serializers.ValidationError('Amount can not be 0')

        return amount

    @staticmethod
    def validate_sender(sender):
        if not Account.objects.filter(account_number=sender).exists():
            raise serializers.ValidationError('Sender account does not exist')

        return sender
