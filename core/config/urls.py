from rest_framework.routers import SimpleRouter

from .views import ConfigViewSet

router = SimpleRouter(trailing_slash=False)
router.register('config', ConfigViewSet)

urlpatterns = router.urls
