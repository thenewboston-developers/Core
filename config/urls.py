from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from blocks.urls import router as block_router

urlpatterns = [
    path('admin/', admin.site.urls),
]

router = DefaultRouter(trailing_slash=False)
router.registry.extend(block_router.registry)

urlpatterns += router.urls
