from rest_framework import serializers
from .models import Address, UserAddresses

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'full_name',
            'address_line_1',
            'address_line_2',
            'city',
            'state_province_region',
            'postal_zip_code',
            'country_region',
            'telephone_number',
        ]

class UserAddressesSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = UserAddresses
        fields = [
            'id',
            'user',
            'address',
        ]