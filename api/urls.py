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
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
# from rest_framework import routers
from rest_framework_nested import routers

from api.auth_user.views import AddUserView, LoginView, UserListView
from api.farmer.views import FarmerViewSet
from api.farm.views import FarmViewSet

router = routers.DefaultRouter()

router.register(r'api/auth/create', AddUserView, basename='create')
router.register(r'api/auth/login', LoginView, basename='login')
router.register(r'api/auth/users', UserListView, basename='users')
router.register(r'api/farmers', FarmerViewSet, basename='farmers')

farmer_router = routers.NestedSimpleRouter(router, r'api/farmers', lookup='farmer')
farmer_router.register(r'farms', FarmViewSet, basename='farmer-farms')
# router.register(r'api/farmers/', FarmerViewSet, basename='farmers')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('api/auth/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),
    path('', include(farmer_router.urls)),
]
