# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse,reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect, render, resolve_url
from django.views import generic
from django.views.generic.list import ListView
from django.db.models.functions import Rank as Ranking
from django.db.models import F, Window

import pandas as pd

from .models import Keyword, Domain, Rank
from .forms import RegisterDomainForm, RegisterKeywordForm
from apps.authentication.forms import NicknameForm
import datetime

def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

class DomainCreate(LoginRequiredMixin,generic.CreateView):
    model = Domain
    form_class = RegisterDomainForm
    template_name = 'home/domain_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = "Domain"
        return context

    def form_valid(self, form):
        """ドメインの登録"""
        domain = form.save(commit=False)
        domain.user = self.request.user
        try:
            domain.save()
            return redirect('dashboard')
        except:
            return redirect('dashboard')





class DashBoardView(LoginRequiredMixin,ListView):
    template_name = 'home/dashboard.html'
    model = Keyword


    def get_queryset(self):
        today = datetime.date.today()
        queryset = Rank.objects.filter(date = today)
        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        domain_list = Domain.objects.filter(user = self.request.user)
        keyword_list = Keyword.objects.filter(domain__in = domain_list)
        context['domain_list'] = domain_list
        context['keyword_list'] = keyword_list

        return context
    
def delete(self, request, **kwargs):
    # まず最初にrankモデルのpkを取得する
    rank_pks = request.POST.getlist('delete_keyword')  # <input type="checkbox" name="delete_keyword"のnameに対応
    rank = Rank.objects.filter(pk__in=rank_pks)
    # 取得したrankモデルを元にrankに紐づくキーワードを特定
    keyword_list = []
    for i in rank:
        keyword_list.append(i.keyword)
    # キーワードを削除
    Keyword.objects.filter(name__in=keyword_list).delete()
    # ドメインの場合はそのまま削除
    domain_pks = request.POST.getlist('delete_domain')  # <input type="checkbox" name="delete_domain"のnameに対応
    Domain.objects.filter(pk__in=domain_pks).delete()

    return redirect('dashboard', pk=self.kwargs['pk'])

class SettingsView(LoginRequiredMixin, generic.FormView):
    form_class = NicknameForm
    template_name = 'home/settings.html'
    success_url = reverse_lazy('settings')

    def get_initial(self):
        initial = super().get_initial()
        initial['nick_name'] = self.request.user.nick_name
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = "settings"
        return context

    def form_valid(self, form):
        
        user = self.request.user
        user.nick_name = form.cleaned_data.get('nick_name')
        user.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('settings')

class KeywordCreate(LoginRequiredMixin, generic.CreateView):
    model = Keyword
    form_class = RegisterKeywordForm
    template_name = 'home/keyword_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = "Keyword"
        return context

    def form_valid(self, form):
        """キーワードの登録"""
        keyword = form.save(commit=False)
        keyword.user = self.request.user
        today = datetime.date.today()
        
        try:
            rank = Rank(keyword = keyword, domain=keyword.domain)
            keyword.save()
            rank.save() 
           
            return redirect('dashboard')
        except:
            return redirect('dashboard')


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.

    load_template = request.path.split('/')[-1]

    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))
    context['segment'] = load_template

    html_template = loader.get_template('home/' + load_template)
    return HttpResponse(html_template.render(context, request))


