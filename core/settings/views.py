from django.http import Http404
from rest_framework.mixins import RetrieveModelMixin

from core.core.views import CustomGenericViewSet, PatchOnlyUpdateModelMixin

from .models import Config
from .serializers import ConfigSerializer


class ConfigViewSet(RetrieveModelMixin, PatchOnlyUpdateModelMixin, CustomGenericViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer

    def get_object(self):
        if self.kwargs['pk'] != 'self':
            raise Http404

        self.kwargs['pk'] = Config.objects.values_list('id', flat=True).get()
        return super().get_object()
