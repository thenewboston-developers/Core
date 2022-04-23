from rest_framework import serializers

from ..models.account import Account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'

    def create(self, validated_data):
        raise RuntimeError('Method unavailable')
