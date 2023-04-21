from django.shortcuts import render
from rest_framework_api.views import BaseAPIView, StandardAPIView
from rest_framework import status
from rest_framework.views import APIView
from django.db import models
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum
# from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.wallet.models import Wallet
from apps.user_profile.models import Profile
from apps.user_profile.serializers import UserProfileSerializer
from .serializers import UserListSerializer,UserSerializer
from apps.wallet.serializers import UserWalletSerializer
from django.http.response import HttpResponse
import json
import uuid
from core.producer import producer
from django.contrib.auth import get_user_model
User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user: User):
        wallet = Wallet.objects.get(user = user)
        user_id = str(user.id)
        token = super().get_token(user)
        token['stripe_customer_id']=user.stripe_customer_id
        token['stripe_account_id']=user.stripe_account_id
        token['stripe_payment_id']=user.stripe_payment_id
        token['user_id']=user_id
        token['username']=user.username
        token['email']=user.email
        token['first_name']=user.first_name
        token['last_name']=user.last_name
        token['agreed']=user.agreed
        token['verified']=user.verified
        token['address']=wallet.address
        token['polygon_address']=wallet.polygon_address
        # token['private_key']=wallet.private_key
        token['role']=user.role
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
# class VerifyAuthentication(StandardAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     def get(self, request, format=None):
#         user = self.request.user
#         if user:        
#             # Get channel layer and group name
#             channel_layer = get_channel_layer()
#             group_name = f'friends_{friend_request.from_user.id}'

#             # Send message to WebSocket group
#             async_to_sync(channel_layer.group_send)(group_name, {
#                 'type': 'send_check_friends',
#                 'is_friend': True
#             })
#             return self.send_response('Success', status=status.HTTP_200_OK)
#         else:
#             return self.send_response('Error, user not authenticated', status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
class RequestInstructorView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, format=None):
        user = self.request.user
        user.become_seller = True
        user.save()
        return self.send_response('Success', status=status.HTTP_200_OK)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)
    
class ListAllUsersView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        user_data = UserListSerializer(users, many=True).data
        return Response(json.dumps(user_data, cls=UUIDEncoder))
    
    
class UserIdListView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, *args, **kwargs):
        # Get user_id list
        user_id_list = User.objects.values_list('id', flat=True)
        # Serialize user_id list
        user_id_list_data = json.dumps(list(user_id_list),cls=UUIDEncoder)
        # Send user_id list to kafka topic
        producer.produce('users_request', key='user_id_list', value=user_id_list_data)
        producer.flush()
        return self.send_response('User id list sent to kafka topic')
    

class GetUserView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id, *args, **kwargs):
        cache_key = f'user_{id}'
        user_data = cache.get(cache_key)

        if not user_data:
            user = User.objects.get(id=id)
            serializer = UserSerializer(user).data
            user_data = serializer
            cache.set(cache_key, user_data, 60 * 15)  # Cache for 15 minutes

        return self.send_response(user_data)

class GetUserProfileView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id, *args, **kwargs):
        cache_key = f'user_profile_{id}'
        profile_data = cache.get(cache_key)
 
        if not profile_data:
            user = User.objects.get(id=id)
            profile = Profile.objects.get(user=user)
            serializer = UserProfileSerializer(profile).data
            profile_data = serializer
            cache.set(cache_key, profile_data, 60 * 15)  # Cache for 15 minutes

        return self.send_response(profile_data)

class GetUserWalletView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id, *args, **kwargs):
        cache_key = f'user_wallet_{id}'
        wallet_data = cache.get(cache_key)

        if not wallet_data:
            user = User.objects.get(id=id)
            wallet = Wallet.objects.get(user=user)
            serializer = UserWalletSerializer(wallet).data
            wallet_data = serializer
            cache.set(cache_key, wallet_data, 60 * 15)  # Cache for 15 minutes

        return self.send_response(wallet_data)


class EditUserRoleView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)
    def put(self, request, *args, **kwargs):
        data = self.request.data
        userId= self.request.data.get('userId')
        user = User.objects.get(id=userId)
        role = self.request.data.get('role')
        user.role = role
        user.save()
        serializer = UserSerializer(user).data
        return self.send_response(serializer)
    

class GetUserProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user.id')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    slug = serializers.CharField(source='user.slug')
    verified = serializers.BooleanField(source='user.verified')
    rating = serializers.SerializerMethodField()
    picture = serializers.ImageField(source='user.profile.picture')
    total_earnings = serializers.DecimalField(source='user.wallet.total_earnings', max_digits=1000, decimal_places=2)

    # Fields from Wallet model
    address = serializers.CharField(source='user.wallet.address')
    polygon_address = serializers.CharField(source='user.wallet.polygon_address')

    is_online = serializers.BooleanField(source='user.is_online')
    
    class Meta:
        model = Profile
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'slug', 'verified', 'rating', 'picture', 'address', 'polygon_address', 'is_online', 'total_earnings']

    def get_rating(self, obj):
        return obj.user.rating.aggregate(models.Avg('rate_number')).get('rate_number__avg', 0)


class GetUserDetailsView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, id, *args, **kwargs):
        user = User.objects.prefetch_related('profile', 'wallet').get(id=id)
        serializer = GetUserProfileSerializer(user.profile)
        return self.send_response(serializer.data)
    

class BestSellingInstructorsView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(role='seller') \
        .annotate(total_earnings=Sum('wallet__total_earnings')) \
        .order_by('-total_earnings')[:10]

        profiles = [user.profile for user in users]
        serializer = GetUserProfileSerializer(profiles, many=True)

        return self.send_response(serializer.data)
    
from django.core.cache import cache

class TestCacheView(StandardAPIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, *args, **kwargs):
        test_key = 'test_key'
        test_value = cache.get(test_key)

        if test_value is None:
            test_value = 'Cache is working!'
            cache.set(test_key, test_value, 60)  # Set cache for 60 seconds
        return self.send_response(test_value)