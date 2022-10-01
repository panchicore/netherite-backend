from accounts.exceptions import AccountMissingException
from accounts.models import Account


def get_queryset_for_account(viewset):
    queryset = viewset.queryset

    # superuser sees everything
    if viewset.request.user.is_superuser:
        return queryset

    # other users only sees what is available on their companies accounts
    account = Account.objects.get_current_account(
        viewset.request.user,
        viewset.request.META.get('HTTP_X_ACCOUNT', '')
    )

    if not account:
        raise AccountMissingException

    queryset = queryset.filter(company=account.company)
    return queryset


def get_account_uuid(serializer):
    return serializer.context["request"].META['HTTP_X_ACCOUNT']
