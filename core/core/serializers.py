from rest_framework.exceptions import ValidationError


class ValidateUnknownFieldsMixin:

    def validate(self, attrs):
        """
        Make front-end developers life easier when they make a typo in an
        optional attribute name.
        """
        attrs = super().validate(attrs)

        # TODO(dmu) MEDIUM: Nested serializers do not have `initial_data` (why?).
        #                   Produce a fix instead of current workaround
        if not hasattr(self, 'initial_data'):
            return attrs

        if unknown_fields := set(self.initial_data).difference(self.fields):
            raise ValidationError(f'Unknown field(s): {", ".join(sorted(unknown_fields))}')

        return attrs


class ValidateReadonlyFieldsMixin:

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # TODO(dmu) HIGH: Nested serializers do not have `initial_data` (why?).
        #                 Produce a fix instead of current workaround
        if not hasattr(self, 'initial_data'):
            return attrs

        readonly_fields = {field_name for field_name, field in self.fields.items() if field.read_only
                           } | set(getattr(self.Meta, 'read_only_fields', ()))

        if readonly_fields := set(self.initial_data).intersection(readonly_fields):
            raise ValidationError(f'Readonly field(s): {", ".join(sorted(readonly_fields))}')

        return attrs


class ValidateFieldsMixin(ValidateUnknownFieldsMixin, ValidateReadonlyFieldsMixin):
    pass
