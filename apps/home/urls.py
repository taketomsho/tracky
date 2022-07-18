# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

app_name="home"
urlpatterns = [
    # ダッシュボード
    path('dashboard/<int:pk>/', views.DashBoardView.as_view(), name='dashboard'),
    # The home page
    path('', views.IndexView.as_view(), name='index'),
    path('<str:job_id>/wait/', views.WaitView.as_view(), name='wait'),
     # ドメイン
    path('domain_update/<int:pk>/', views.DomainUpdate.as_view(), name='domain_update'),
     # キーワード
    path('keyword_update/<int:pk>/', views.KeywordUpdate.as_view(), name='keyword_update'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
     
]
