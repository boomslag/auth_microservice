from djoser.serializers import UserCreateSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


from django.contrib.auth import get_user_model
User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        return data

class UserSerializer(UserCreateSerializer):
    student_rating=serializers.IntegerField(source='get_rating')
    student_rating_no=serializers.IntegerField(source='get_no_rating')
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            'id',
            'stripe_customer_id',
            'stripe_account_id',
            'stripe_payment_id',
            'email',
            'username',
            'slug',
            'first_name',
            'last_name',
            'agreed',
            'is_active',
            'is_staff',
            'become_seller',
            'role',
            'verified',
            'student_rating',
            'student_rating_no',
            'students',
            'courses',
            'earned',
            'products',
            'sellerAcceptedTerms',
            'buyers',
            'is_online',
        ]

class UserListSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            'id',
            'stripe_customer_id',
            'stripe_account_id',
            'stripe_payment_id',
            'email',
            'is_active',
            'username',
            'verified',
            'become_seller',
            'is_online',
        ]