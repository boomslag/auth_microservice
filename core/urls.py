from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from apps.user.views import CustomTokenObtainPairView

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    path('auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='custom_jwt_create'),

    path('api/users/', include('apps.user.urls')),
    path('api/friends/', include('apps.friends.urls')),
    path('api/delivery/', include('apps.delivery.urls')),
    path('api/contacts/', include('apps.contacts.urls')),
    path('api/profiles/', include('apps.user_profile.urls')),
    path('api/wallets/', include('apps.wallet.urls')),

    path('admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
