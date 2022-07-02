# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, UserCreate, PasswordReset, PasswordResetDone, PasswordResetConfirm, PasswordResetComplete, EmailChange, EmailChangeDone, EmailChangeComplete, PasswordChange, PasswordChangeDone, UserCreateDone, UserCreateComplete, Withdraw, WithdrawDone
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', UserCreate.as_view(), name="register"),
    path('register/done', UserCreateDone.as_view(), name="user_create_done"),
    path('register/complete/<token>/', UserCreateComplete.as_view(), name="user_create_complete"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('password_change/', PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDone.as_view(), name='password_change_done'),
    path("passwordreset/", PasswordReset.as_view(), name="passwordreset"),
    path("passwordreset/done/", PasswordResetDone.as_view(), name="password_reset_done"),
    path('password_reset/confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('email/change/', EmailChange.as_view(), name='email_change'),
    path('email/change/done/', EmailChangeDone.as_view(), name='email_change_done'),
    path('email/change/complete/<str:token>/', EmailChangeComplete.as_view(), name='email_change_complete'),
    path('withdraw/', Withdraw.as_view(), name='withdraw'),
    path('withdraw/done/', WithdrawDone, name='withdraw_done'),

]
