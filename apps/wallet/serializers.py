from rest_framework import serializers
from .models import *

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'id',
            'address',
            'polygon_address',
            'savings',
            'total_earnings',
            'total_spent',
            'total_transfered',
            'total_received',
            'product_sales',
            'course_sales',
        ]

class UserWalletPrivateKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'id',
            'address',
            'polygon_address',
            'private_key',
            'polygon_private_key',
            'savings',
            'total_earnings',
            'total_spent',
            'total_transfered',
            'total_received',
            'product_sales',
            'course_sales',
        ]
