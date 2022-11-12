from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from accounts.permissions import AccountsPermission
from netherite.utils.api import get_queryset_for_account
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    """

    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, AccountsPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type']
    search_fields = ['plate']

    def get_queryset(self):
        queryset = get_queryset_for_account(self)

        if self.request.user.groups.contains(Group.objects.get(name='Drivers')):
            # TODO: Driver vehicles
            queryset = queryset

        if self.request.user.groups.contains(Group.objects.get(name='Vehicle Owners')):
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        super().perform_create(serializer)
