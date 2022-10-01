from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response

from accounts.models import Account
from accounts.permissions import AccountsPermission
from accounts.serializers import AccountSerializer, UserSerializer
from drivers.models import Driver, DriverDocument
from drivers.serializers import DriverSerializer, DriverUserSerializer, DriverDocumentSerializer
from netherite.utils.api import get_queryset_for_account


class DriverViewSet(viewsets.ModelViewSet):
    """
    Company's drivers.

    An user only can create:
        drivers using their company pk.
        unique identification for ids.

    """
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, AccountsPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['identification_type']
    search_fields = ['first_name', 'last_name', 'identification']

    def get_queryset(self):
        queryset = get_queryset_for_account(self)
        if self.request.user.groups.contains(Group.objects.get(name='Drivers')):
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        super().perform_create(serializer)

    @action(detail=True, methods=['post'])
    def user(self, request, pk=None):
        driver = self.get_object()
        serializer = DriverUserSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)

        email = serializer.validated_data["email"]
        username = email.split("@")[0]
        # get or create the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=driver.first_name,
                last_name=driver.last_name
            )

        # add to the drivers group
        drivers_group = Group.objects.get(name__iexact="Drivers")
        user.groups.add(drivers_group)
        user.save()

        # create an account
        account, _ = Account.objects.associate(user, driver.company)

        # associate it with the driver
        driver.user = user
        driver.save()
        driver.notify_to_driver_user()

        driver_serializer = DriverSerializer(driver)
        account_serializer = AccountSerializer(account)
        user_serializer = UserSerializer(user)

        return Response({
            "user": user_serializer.data,
            "driver": driver_serializer.data,
            "account": account_serializer.data,
        })


class DriverDocumentViewSet(viewsets.ModelViewSet):
    """
    Driver's documents files.

    A driver or coordinator only can create:
        driver documents within their company.

    """
    queryset = DriverDocument.objects.all()
    serializer_class = DriverDocumentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions,
                          AccountsPermission]

    def get_queryset(self):
        queryset = get_queryset_for_account(self)
        if self.request.user.groups.contains(Group.objects.get(name='Drivers')):
            queryset = queryset.filter(driver__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        super().perform_create(serializer)


