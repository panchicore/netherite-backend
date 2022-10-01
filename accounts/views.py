from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from accounts.models import Company, Account
from accounts.permissions import AccountsPermission
from accounts.serializers import CompanySerializer, UserSerializer, AccountSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = UserSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Companies are better created on the admin site.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUser]


class AccountViewSet(viewsets.ModelViewSet):
    """
    Accounts of the logged in user
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)





