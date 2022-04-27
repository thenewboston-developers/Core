from rest_framework import mixins, viewsets

UPDATE_METHODS = frozenset(('PATCH', 'PUT'))


class CustomGenericViewSet(viewsets.GenericViewSet):

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method in UPDATE_METHODS:
            queryset = queryset.select_for_update()

        return queryset


class PatchOnlyUpdateModelMixin(mixins.UpdateModelMixin):
    # PUT method should be disabled if we allow modification only subset of
    # attributes of a resource once or/and we do not allow
    # to resource id for creation (a special case of PUT)
    # TODO(dmu) LOW: Provide a better way to disable PUT
    # (by modifying action_map)
    http_method_names = [name for name in CustomGenericViewSet.http_method_names if name != 'put']
