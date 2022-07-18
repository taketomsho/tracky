# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

app_name="home"
urlpatterns = [
    # ダッシュボード
    path('dashboard', views.DashBoardView.as_view(), name='dashboard'),
    # The home page
    path('', views.IndexView.as_view(), name='index'),
    path('<str:job_id>/wait/', views.WaitView.as_view(), name='wait'),
     # ドメイン
    path('domain_create', views.DomainCreate.as_view(), name='domain_create'),
     # キーワード
    path('keyword_create', views.KeywordCreate.as_view(), name='keyword_create'),
    path('settings', views.SettingsView.as_view(), name='settings'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
     
]
