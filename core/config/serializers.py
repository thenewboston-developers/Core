from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.core.constants import ACCOUNT_NUMBER_LENGTH, SIGNATURE_LENGTH
from core.core.serializers import ValidateFieldsMixin
from core.core.utils.cryptography import is_dict_signature_valid
from core.core.validators import HexStringValidator

from .models import Config


class ConfigSerializer(ValidateFieldsMixin, serializers.ModelSerializer):

    account_number = serializers.CharField(
        min_length=ACCOUNT_NUMBER_LENGTH,
        max_length=ACCOUNT_NUMBER_LENGTH,
        validators=(HexStringValidator(ACCOUNT_NUMBER_LENGTH),),
        write_only=True,
        required=True
    )
    signature = serializers.CharField(
        min_length=SIGNATURE_LENGTH,
        max_length=SIGNATURE_LENGTH,
        validators=(HexStringValidator(SIGNATURE_LENGTH),),
        write_only=True,
        required=True
    )

    class Meta:
        model = Config
        fields = ('account_number', 'signature', 'owner', 'transaction_fee')

    def validate(self, attrs):
        # TODO(dmu) MEDIUM: Consider DRYing up with core.accounts.serializers.account.AccountSerializer.validate()
        #                   Or implementation of Authorization HTTP-header based signing
        attrs = super().validate(attrs)

        owner = self.instance.owner
        if not owner:
            raise ValidationError('Owner must be configured.')

        signature = attrs.pop('signature', None)
        if not signature:
            # The signature is required even for partial updates (PATCH-requests) therefore we have to validate
            # it explicitly hereF
            raise ValidationError({'signature': ['This field is required.']})

        account_number = attrs.get('account_number')
        if not account_number:
            # The account_number is required even for partial updates (PATCH-requests) therefore we have to validate
            # it explicitly here
            raise ValidationError({'account_number': ['This field is required.']})

        if account_number != owner:
            raise ValidationError({'account_number': ['Must be owner.']})

        if not is_dict_signature_valid(attrs, account_number, signature):
            raise ValidationError({'signature': ['Invalid.']})

        return attrs
