from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from clients.models import Client
from clients.serializers import ClientSerializer
from netherite.utils.api import get_queryset_for_account


class ClientViewSet(viewsets.ModelViewSet):
    """
    Company's clients.

    An user only can create:
        clients using their company pk.
        unique names.

    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    # view model permissions hack https://stackoverflow.com/a/46585240/155293

    def get_queryset(self):
        return get_queryset_for_account(self)

    def perform_update(self, serializer):
        # serializer.save(updated_by=self.request.user)
        super().perform_update(serializer)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        super().perform_create(serializer)
