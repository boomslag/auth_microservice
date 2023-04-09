from django.urls import path

from .views import *


urlpatterns = [
    path('get_addresses/', GetUserAddresses.as_view()),
    # path('test_paginated', HelloWorldPaginatedView.as_view()),
    # path('category/<category_slug>', BlogListCategoryView.as_view()),
    # path('<post_slug>', PostDetailView.as_view()),
    # path("search/<str:search_term>",SearchBlogView.as_view()),
]