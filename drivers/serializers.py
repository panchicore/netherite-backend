from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from drivers.models import Driver, DriverDocument


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = "__all__"
        validators = [
            # Validate only one client with the same name per client
            UniqueTogetherValidator(
                queryset=Driver.objects.all(),
                fields=['identification', 'identification_type', 'company']
            )
        ]


class DriverUserSerializer(serializers.Serializer):
    email = serializers.EmailField()


class DriverDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDocument
        fields = "__all__"

    def validate_driver(self, driver):
        """
        Validate only drivers associated with the company's accounts.
        :param driver:
        :return:
        """
        company_id = self.context['request'].POST['company']
        if not Driver.objects.filter(company_id=company_id, id=driver.id).exists():
            raise serializers.ValidationError('Driver not driving for the company')

        return driver
