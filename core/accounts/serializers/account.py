from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.core.constants import SIGNATURE_LENGTH
from core.core.serializers import ValidateFieldsMixin
from core.core.utils.cryptography import is_dict_signature_valid
from core.core.validators import HexStringValidator

from ..models.account import Account


class AccountSerializer(ValidateFieldsMixin, serializers.ModelSerializer):

    signature = serializers.CharField(
        min_length=SIGNATURE_LENGTH,
        max_length=SIGNATURE_LENGTH,
        validators=(HexStringValidator(SIGNATURE_LENGTH),),
        write_only=True,
        required=True
    )

    class Meta:
        model = Account
        fields = ('account_number', 'avatar', 'balance', 'display_name', 'signature')
        read_only_fields = (
            'account_number',
            'balance',
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        signature = attrs.pop('signature', None)
        if not signature:
            # The signature is required even for partial updates (PATCH-requests) therefore we have to validate
            # it explicitly here
            raise ValidationError({'signature': ['This field is required.']})

        if not is_dict_signature_valid(attrs, self.instance.account_number, signature):
            raise ValidationError({'signature': ['Invalid.']})

        return attrs
