from django.urls import path

from .views import *


urlpatterns = [
    path('my_wallet', MyUserWalletView.as_view()),
    path('get/', GetUserWalletView.as_view()),
    path('get_polygon/', GetUserPolygonWalletView.as_view()),
    path('my_balance', MyUserWalletBalanceView.as_view()),
    path('pdm_balance', GetPraediumBalanceView.as_view()),
    path('galr_balance', GetGalacticReserveBalanceView.as_view()),
    # path('<post_slug>', PostDetailView.as_view()),
    # path("search/<str:search_term>",SearchBlogView.as_view()),
]