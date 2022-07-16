# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Domain,Keyword,Rank

# Register your models here.

admin.site.register(Domain)
admin.site.register(Keyword)
admin.site.register(Rank)