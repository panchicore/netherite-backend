from django.db import models
from rest_framework.exceptions import APIException

from accounts.exceptions import AccountMissingException


class AccountManager(models.Manager):
    def associate(self, user, company):
        """
        Create the account for the user on this company
        :param user:
        :param company:
        :return:
        """

        account, new = self.get_or_create(
            user=user,
            company=company
        )

        return account, new

    def is_associated(self, user, company):
        """
        Is this user associated with this company?
        :param user:
        :param company:
        :return: boolean
        """
        return self.filter(
            user=user,
            company=company
        ).exists()

    def has(self, user, uuid):
        """
        Is this user associated with this account uuid?
        :param user:
        :param uuid:
        :return:
        """
        return self.filter(user=user, uuid=uuid).exists()

    def get_current_account(self, user, uuid):
        """
        Get the user's current account.
        :param user:
        :param uuid: coming from HTTP_X_ACCOUNT
        :return:
        """

        try:
            return self.get(user=user, uuid=uuid)
        except Exception as e:
            return None
