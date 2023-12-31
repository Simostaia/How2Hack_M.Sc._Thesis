# -*- encoding: utf-8 -*-
"""
CyberHackAdemy 2021
"""

from django.urls import path
from .views import login_view, logout_view, register_user
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    # path("logout/", LogoutView.as_view(), name="logout")
    path("logout/", logout_view, name="logout")
]
