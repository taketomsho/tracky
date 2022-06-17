# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.contrib.auth import get_user_model

# Create your models here.


class Domain(models.Model):
    name = models.CharField(max_length=500)
    user = models.ForeignKey(get_user_model(), on_delete=CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"],
                name="domain_unique"
            ),
        ]

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=500)
    domain = models.ForeignKey(Domain, on_delete=CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "domain"],
                name="keyword_unique"
            ),
        ]
    def __str__(self):
        return self.name