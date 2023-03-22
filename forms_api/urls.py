from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Own Forms",
        default_version='v1',
        description="Create your own forms",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@mail.com"),
      license=openapi.License(name="License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('forms/', include('own_forms.urls')),
    path('auth2/', include('auth2.urls')),
    path('', schema_view.with_ui('swagger', 
                                cache_timeout=0), name='schema-swagger-ui'),
]
