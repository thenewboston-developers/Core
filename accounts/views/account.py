from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from ..models.account import Account
from ..serializers.account import AccountSerializer


class AccountViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
