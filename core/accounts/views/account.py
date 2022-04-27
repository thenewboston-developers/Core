from rest_framework.mixins import RetrieveModelMixin

from core.core.views import CustomGenericViewSet, PatchOnlyUpdateModelMixin

from ..models.account import Account
from ..serializers.account import AccountSerializer


class AccountViewSet(RetrieveModelMixin, PatchOnlyUpdateModelMixin, CustomGenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
