from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from accounts.views import CompanyViewSet, AccountViewSet
from clients.views import ClientViewSet
from drivers.views import DriverViewSet, DriverDocumentViewSet

router = routers.DefaultRouter()
router.register(r'accounts/companies', CompanyViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'drivers/docs', DriverDocumentViewSet)
router.register(r'drivers', DriverViewSet)

urlpatterns = [
    path('api/1/', include(router.urls)),
    path('nimda/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('activity/', include('actstream.urls'))
]
