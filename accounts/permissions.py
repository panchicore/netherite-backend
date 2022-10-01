from rest_framework import permissions

from accounts.exceptions import AccountNotAssociatedException, CompanyMissingException, AccountMissingException
from accounts.models import Account


class AccountsPermission(permissions.BasePermission):
    """
    Global permission check for user's account
    """

    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True

        account_uuid = request.META.get("HTTP_X_ACCOUNT", "")

        has_account = Account.objects.has(user=request.user, uuid=account_uuid)
        if not has_account:
            raise AccountMissingException

        if request.method in ["GET"]:
            return True

        company_id = request.POST.get('company', request.data.get('company'))
        if not company_id:
            raise CompanyMissingException

        association = Account.objects.filter(user=request.user, company_id=company_id).exists()
        if not association:
            raise AccountNotAssociatedException

        return True

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
