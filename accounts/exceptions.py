from rest_framework.exceptions import APIException


class AccountMissingException(APIException):
    status_code = 403
    default_detail = 'Account is missing for the requesting user. ' \
                     'Use \'X-ACCOUNT\' http headers with valid account UUID to identify user\'s current account.'
    default_code = 'account_missing'


class AccountNotAssociatedException(APIException):
    status_code = 403
    default_detail = 'You do not have the account associated with the company to perform this action.'
    default_code = 'account_not_associated'


class CompanyMissingException(APIException):
    status_code = 400
    default_detail = 'Request must send the company on the payload.'
    default_code = 'company_missing'
