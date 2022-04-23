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
        try:
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
            raise serializers.ValidationError(e)

        return block

    def update(self, instance, validated_data):
        raise RuntimeError('Method unavailable')

    def validate(self, data):
        data = super(BlockSerializerCreate, self).validate(data)
        sender = data['sender']
        recipient = data['recipient']
        amount = data.get('amount')

        if sender == recipient:
            raise serializers.ValidationError('Sender and recipient can not be the same')

        if amount is not None:
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
        sender_account = Account.objects.filter(account_number=sender).first()

        if sender_account is None:
            raise serializers.ValidationError('Sender account does not exist')

        return sender
