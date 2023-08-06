import importlib

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, path

from rest_framework.authtoken.views import obtain_auth_token

from huscy_project.views import health_check


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    path('health_check/', health_check),
    path('api-auth-token/', obtain_auth_token),
]

if settings.DEBUG:
    urlpatterns.append(
        path('api-auth/', include('rest_framework.urls')),
    )

for app in apps.get_app_configs():
    if hasattr(app, 'HuscyAppMeta'):
        try:
            importlib.import_module(f'{app.name}.urls')
        except ImportError:
            continue
        urlpatterns.append(path('api/', include(f'{app.name}.urls')))
