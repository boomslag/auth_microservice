from django.urls import path

from .views import *


urlpatterns = [
    path('instructor/request/', RequestInstructorView.as_view()),
    path('list/', ListAllUsersView.as_view()),
    path('list/ids/', UserIdListView.as_view()),
    path('get/<id>/', GetUserView.as_view()),
    path('get_details/<id>/', GetUserDetailsView.as_view()),
    path('get/profile/<id>/', GetUserProfileView.as_view()),
    path('get/wallet/<id>/', GetUserWalletView.as_view()),
    path('instructors/best_selling/', BestSellingInstructorsView.as_view(), name='best_selling_instructors'),
    path('test_cache/', TestCacheView.as_view()),
    # path('<post_slug>', PostDetailView.as_view()),
    # path("search/<str:search_term>",SearchBlogView.as_view()),
]