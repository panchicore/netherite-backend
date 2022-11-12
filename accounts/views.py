from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import Company, Account
from accounts.serializers import CompanySerializer, UserSerializer, AccountSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = UserSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset

        # list only companies associated to the user
        companies = Account.objects.filter(user=self.request.user).values_list("company_id", flat=True)
        return self.queryset.filter(id__in=companies)


class AccountViewSet(viewsets.ModelViewSet):
    """
    Accounts of the logged in user
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
