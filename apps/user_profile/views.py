
from django.core.exceptions import ValidationError
import base64
import secrets
from rest_framework_api.views import BaseAPIView, StandardAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from slugify import slugify
from apps.wallet.models import Wallet
from django.contrib.auth import get_user_model
from django.conf import settings
from base64 import b64decode
from django.core.files.base import ContentFile
import os
from web3 import Web3
from django.core.cache import cache
from django.shortcuts import get_object_or_404
import re
User = get_user_model()
infura_url=settings.INFURA_URL
web3 = Web3(Web3.HTTPProvider(infura_url))

from .models import Profile
from .serializers import UserProfileSerializer


pattern_special_characters = r'\badmin\b|[!@#$%^&*()_+-=[]{}|;:",.<>/?]|\s'

class MyUserProfileView(APIView):
    def get(self,request,*args, **kwargs):
        # Generate the response data
        user = self.request.user
        profile = Profile.objects.get(user=user)
        serializer = UserProfileSerializer(profile)
        return Response({'profile':serializer.data},status=status.HTTP_200_OK)


class DetailUserProfileView(StandardAPIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)
        wallet = Wallet.objects.get(user=user)

        user_data = {
            'id':user.id,
            'username':username,
            'email':user.email,
            'picture':profile.picture.url,
            'banner':profile.banner.url,
            'location':profile.location,
            'url':profile.url,
            'birthday':profile.birthday,
            'profile_info':profile.profile_info,
            'role':user.role,
            'verified':user.verified,
            'address':wallet.address,
            'facebook':profile.facebook,
            'twitter':profile.twitter,
            'instagram':profile.instagram,
            'linkedin':profile.linkedin,
            'youtube':profile.youtube,
            'github':profile.github,
        }

        return self.send_response(user_data,status=status.HTTP_200_OK)


class EditUsernameView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        user_model = User.objects.get(id=user.id)
        
        username = data['username']

        pattern = r'\badmin\b|[!@#$%^&*()_+-=[]{}|;:",.<>/?]|\s'

        if re.search(pattern, username, re.IGNORECASE) is None:

            user_model.username = username
            user_model.slug = username
            user_model.save()
            
            return self.send_response('Success',status=status.HTTP_200_OK)
        else:
            return self.send_error('Error',500)

class EditProfilePictureView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, format=None):
        image = request.POST.get('image')
        filename = request.POST.get('filename')

        # print(f"Image: {image}")
        # print(f"Filename: {filename}")

        # Define User
        user = request.user
        # print(f"User: {user}")

        # Retrieve the user's profile
        profile = user.profile

        allowed_extensions = ['jpeg', 'jpg', 'png']

        if ';base64,' in image:
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr))

            # Generate a unique file name
            file_name, file_ext = os.path.splitext(filename)
            unique_name = f"{file_name}_{secrets.token_hex(8)}{file_ext}"
            data.name = unique_name

            # print(f"Generated unique name: {unique_name}")

            # validate the file type
            if ext not in allowed_extensions:
                raise ValidationError('Invalid file type. Only jpeg and png are allowed.')

            # validate the file size
            if data.size > 2000000:
                raise ValidationError('File size should be less than 2MB')

            profile.picture = data
        elif image.startswith('/media/') or image.startswith('http'):
            # Validate the file type based on the URL
            file_name, file_ext = os.path.splitext(image)
            if file_ext[1:] not in allowed_extensions:
                raise ValidationError('Invalid file type. Only jpeg and png are allowed.')
        else:
            raise ValidationError('Invalid image file format.')

        profile.save()
        # print(f"Profile picture after save: {profile.picture}")

        return self.send_response('Success', status=status.HTTP_200_OK)

class EditBannerView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, format=None):
        image = request.POST.get('image')
        filename = request.POST.get('filename')

        # print(f"Image: {image}")
        # print(f"Filename: {filename}")

        # Define User
        user = request.user
        # print(f"User: {user}")

        # Retrieve the user's profile
        profile = user.profile

        allowed_extensions = ['jpeg', 'jpg', 'png']

        if ';base64,' in image:
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr))

            # Generate a unique file name
            file_name, file_ext = os.path.splitext(filename)
            unique_name = f"{file_name}_{secrets.token_hex(8)}{file_ext}"
            data.name = unique_name

            # print(f"Generated unique name: {unique_name}")

            # validate the file type
            if ext not in allowed_extensions:
                raise ValidationError('Invalid file type. Only jpeg and png are allowed.')

            # validate the file size
            if data.size > 2000000:
                raise ValidationError('File size should be less than 2MB')

            profile.banner = data
        elif image.startswith('/media/') or image.startswith('http'):
            # Validate the file type based on the URL
            file_name, file_ext = os.path.splitext(image)
            if file_ext[1:] not in allowed_extensions:
                raise ValidationError('Invalid file type. Only jpeg and png are allowed.')
        else:
            raise ValidationError('Invalid image file format.')

        profile.save()
        # print(f"Profile banner after save: {profile.banner}")

        return self.send_response('Success', status=status.HTTP_200_OK)

class EditFirstNameView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        user_model = User.objects.get(id=user.id)
        
        first_name = data['first_name']

        user_model.first_name = first_name
        user_model.save()
        return Response({
            'success':'UserAccount Edited' 
        },status=status.HTTP_200_OK)

class EditLastNameView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        user_model = User.objects.get(id=user.id)
        
        last_name = data['last_name']

        user_model.last_name = last_name
        user_model.save()
        return Response({
            'success':'UserAccount Edited' 
        },status=status.HTTP_200_OK)


class EditUserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        user_model = User.objects.get(id=user.id)

        profile = Profile.objects.get(id=user.id)

        
        picture = data['picture']
        banner = data['banner']

        location = data['location']
        url = data['url']
        birthday = data['birthday']
        profile_info = data['profile_info']
        facebook = data['facebook']
        twitter = data['twitter']
        instagram = data['instagram']
        linkedin = data['linkedin']
        youtube = data['youtube']
        github = data['github']
        # agreed = data['agreed']

        if(location !=''):
            profile.location = location
            profile.save()

        if(url !=''):
            profile.url = url
            profile.save()

        if(picture !=''):
            user_model.picture = picture
            user_model.save()

        if(banner !=''):
            user_model.banner = banner
            user_model.save()
            
        if(birthday !=''):
            profile.birthday = birthday
            profile.save()

        if(profile_info !=''):
            profile.profile_info = profile_info
            profile.save()

        # Social Edit
        if(facebook !=''):
            profile.facebook = facebook
            profile.save()
        if(twitter !=''):
            profile.twitter = twitter
            profile.save()
        if(instagram !=''):
            profile.instagram = instagram
            profile.save()
        if(linkedin !=''):
            profile.linkedin = linkedin
            profile.save()
        if(youtube !=''):
            profile.youtube = youtube
            profile.save()
        if(github !=''):
            profile.github = github
            profile.save()
        
        # user_model.agreed = agreed
        # user_model.save()
        

        return Response({
            'success':'UserAccount Edited' 
        },status=status.HTTP_200_OK)


class EditUserLocationView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user

        profile = Profile.objects.get(user=user)

        location = data['location']
        # agreed = data['agreed']

        profile.location = location
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)


class EditUserURLView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        url = data['url']
        # agreed = data['agreed']

        profile.url = url
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)


class EditUserBirthDayView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        birthday = data['birthday']
        # agreed = data['agreed']

        profile.birthday = birthday
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)


class EditUserBioView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user

        profile_info = data['profile_info']

        profile = Profile.objects.get(user=user)

        profile.profile_info = profile_info
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)

class EditUserProfessionView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user

        profession = data['profession']

        profile = Profile.objects.get(user=user)

        profile.profession = profession
        user.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)


class EditUserFacebookView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        facebook = data['facebook']

        profile.facebook = facebook
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)

class EditUserTwitterView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        twitter = data['twitter']

        profile.twitter = twitter
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)

class EditUserInstagramView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        instagram = data['instagram']

        profile.instagram = instagram
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)

class EditUserLinkedInView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        linkedin = data['linkedin']

        profile.linkedin = linkedin
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)


class EditUserYouTubeView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        youtube = data['youtube']

        profile.youtube = youtube
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)


class EditUserGithubView(StandardAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self,request,format=None):

        data = self.request.data
        # Define User
        user = self.request.user
        profile = Profile.objects.get(user=user)

        github = data['github']

        profile.github = github
        profile.save()
        
        return self.send_response('Success',status=status.HTTP_200_OK)

