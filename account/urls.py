from django.urls import path
from .views import *
urlpatterns=[
    path('signup/',SignupView.as_view(),name='signup'),
    path('logout/',custom_logout, name='logout'),
]