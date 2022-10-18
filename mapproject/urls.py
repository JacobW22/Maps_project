from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from map import views as map_views


schema_view = get_schema_view(
   openapi.Info(
      title="Shop Finder API",
      default_version='v1',
     # url='https://example.net/api/v1/',
      description="Free api of the Shop Finder app",
      contact=openapi.Contact(email="jwis02202@gmail.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', map_views.index, name='index'),
    path('api/all_shops/', map_views.ShoplistAPIView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/chosen_shops/$', map_views.ShopFinderAPIView.as_view(), name='combined-list'),
    re_path(r'^api/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

]
