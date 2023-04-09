from rest_framework import status
from rest_framework.response import Response
from rest_framework_api.views import StandardAPIView
from rest_framework import permissions
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *
from .serializers import *
import json
from django.core.exceptions import ObjectDoesNotExist


class GetUserAddresses(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        try:
            addresses = UserAddresses.objects.get(user=user)
            serializer = UserAddressesSerializer(addresses).data
            return self.send_response(serializer)
        except UserAddresses.DoesNotExist:
            return self.send_error('No delivery addresses found for the user.')