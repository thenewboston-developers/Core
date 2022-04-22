from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts.urls import router as account_router
from blocks.urls import router as block_router

urlpatterns = [
    path('admin/', admin.site.urls),
]

router = DefaultRouter(trailing_slash=False)
router.registry.extend(account_router.registry)
router.registry.extend(block_router.registry)

urlpatterns += router.urls
