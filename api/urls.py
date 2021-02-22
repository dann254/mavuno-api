"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt import views as jwt_views
# from rest_framework import routers
from rest_framework_nested import routers
from django.conf import settings
from django.conf.urls.static import static

from api.auth_user.views import AddUserView, LoginView, UserListView, UserView
from api.farmer.views import FarmerViewSet
from api.farm.views import FarmViewSet
from api.harvest.views import HarvestViewSet


schema_view = get_schema_view(
   openapi.Info(
      title="Mavuno API",
      default_version='v1',
      description="Mavuno is a product that allows collection of data about farmers, farms and their harvests.",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()

router.register(r'api/auth/create', AddUserView, basename='create')
router.register(r'api/auth/login', LoginView, basename='login')
router.register(r'api/auth/users', UserListView, basename='users')
router.register(r'api/auth/user', UserView, basename='user')
router.register(r'api/farmers', FarmerViewSet, basename='farmers')

farmer_router = routers.NestedSimpleRouter(router, r'api/farmers', lookup='farmer')
farmer_router.register(r'farms', FarmViewSet, basename='farmer-farms')

farm_router = routers.NestedSimpleRouter(farmer_router, r'farms', lookup='farm')
farm_router.register(r'harvests', HarvestViewSet, basename='farmer-farms-harvest')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('api/auth/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),
    path('', include(farmer_router.urls)),
    path('', include(farm_router.urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
