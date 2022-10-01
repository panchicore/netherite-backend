from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from accounts.models import Account
from clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        validators = [
            # Validate only one client with the same name per client
            UniqueTogetherValidator(
                queryset=Client.objects.all(),
                fields=['name', 'company']
            )
        ]

    def validate_company(self, company):
        """
        Validate only companies associated with the user's accounts.
        :param company:
        :return:
        """
        user = self.context['request'].user
        if not Account.objects.is_associated(user, company):
            raise serializers.ValidationError('Company not part of user accounts')
        return company
