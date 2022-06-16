# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
   
    # The home page
    path('', views.index, name='home'),
     # ドメイン
    path('domain_list/<int:pk>/', views.DomainListView.as_view(), name='domain_list'),
    path('domain_update/<int:pk>/', views.DomainUpdate.as_view(), name='domain_update'),
     # キーワード
    path('keyword_list/<int:pk>/', views.KeywordListView.as_view(), name='keyword_list'),
    path('keyword_update/<int:pk>/', views.KeywordUpdate.as_view(), name='keyword_update'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
     
]
