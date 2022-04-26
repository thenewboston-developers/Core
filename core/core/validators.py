from django.core.validators import RegexValidator


class HexStringValidator(RegexValidator):

    def __init__(self, length: int):
        super().__init__(regex='^[0-9a-f]{%s}$' % length)
