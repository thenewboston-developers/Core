from rest_framework import serializers

from ..models.account import Account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('account_number', 'avatar', 'balance', 'display_name')
        read_only_fields = (
            'account_number',
            'balance',
        )

    def create(self, validated_data):
        # TODO(dmu) HIGH: Introduce a better way of disabling account creation
        #                 https://github.com/thenewboston-developers/Core/issues/23
        raise RuntimeError('Method unavailable')
