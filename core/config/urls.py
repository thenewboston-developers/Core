from django.contrib import admin
from django.urls import include, path

import core.accounts.urls
import core.blocks.urls
import core.settings.urls

API_PREFIX = 'api/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(API_PREFIX, include(core.accounts.urls)),
    path(API_PREFIX, include(core.blocks.urls)),
    path(API_PREFIX, include(core.settings.urls)),
]
