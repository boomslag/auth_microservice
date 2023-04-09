from django.urls import path

from .views import *


urlpatterns = [
    path('my_profile', MyUserProfileView.as_view()),
    path('get/<username>', DetailUserProfileView.as_view()),

    path('edit/username', EditUsernameView.as_view()),
    path('edit/picture', EditProfilePictureView.as_view()),
    path('edit/banner', EditBannerView.as_view()),
    path('edit/first_name', EditFirstNameView.as_view()),
    path('edit/last_name', EditLastNameView.as_view()),
    path('edit/location', EditUserLocationView.as_view()),
    path('edit/url', EditUserURLView.as_view()),
    path('edit/birthday', EditUserBirthDayView.as_view()),
    path('edit/bio', EditUserBioView.as_view()),
    path('edit/profession', EditUserProfessionView.as_view()),
    path('edit/facebook', EditUserFacebookView.as_view()),
    path('edit/twitter', EditUserTwitterView.as_view()),
    path('edit/instagram', EditUserInstagramView.as_view()),
    path('edit/linkedin', EditUserLinkedInView.as_view()),
    path('edit/youtube', EditUserYouTubeView.as_view()),
    path('edit/github', EditUserGithubView.as_view()),
]