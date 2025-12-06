from django.contrib import admin
from django.urls import path, include, re_path
import logging
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve

schema_view = get_schema_view(
    openapi.Info(
        title="Edu NeoSoft API",
        default_version='v1',
        description="Edu NeoSoft API documentation",
        terms_of_service="https://edu.neosoft.uz/",
        contact=openapi.Contact(email="dilshod.normurodov1392@gmail.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)



urlpatterns = [
    re_path(r'^api/swagger/(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += i18n_patterns(
    path('api/i18n/', include('django.conf.urls.i18n')),
    path('api/admin/', admin.site.urls),
    path('api/authentication/', include('authentication.urls')),
    path('api/authentication/manager/', include('authentication.manager.urls')),
    path('api/mentor/', include('authentication.mentors.urls')),
    path('api/content/', include('content.urls')),
    path('api/payment/', include('payment.urls')),
    prefix_default_language=False
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    path("media/<path:path>", serve, {"document_root": settings.PRIVATE_CONTRACT_ROOT}),
]

if settings.DEBUG:
       import debug_toolbar
       urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]