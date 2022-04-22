from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from ..models.account import Account
from ..serializers.account import AccountSerializer


class AccountViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
