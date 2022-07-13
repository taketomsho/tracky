# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, render, resolve_url
from django.views import generic
from django.views.generic.list import ListView

import pandas as pd

from .models import Keyword, Domain, Rank
from .forms import RegisterDomainForm, RegisterKeywordForm
import datetime

def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser

class DomainUpdate(OnlyYouMixin, generic.CreateView):
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
        domain.user_id = self.kwargs['pk']
        try:
            domain.save()
            return redirect('dashboard', pk=self.kwargs['pk'])
        except:
            return redirect('dashboard', pk=self.kwargs['pk'])

        

class DashBoardView(OnlyYouMixin, ListView):
    template_name = 'home/dashboard.html'
    model = Rank
    queryset = Rank.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        domain = Domain.objects.filter(user=self.kwargs['pk'])
        # rank = Rank.objects.filter(user=self.kwargs['pk'])
        context["domain"] = domain

        # 日付を1週間分取得
        # date_index = pd.date_range(today, periods=7, freq="D")
        date_list = [datetime.date.today() - datetime.timedelta(days=i) for i in range(10)]
        print(date_list)
        context["date_list"] = date_list
            
        return context

    def post(self, request, **kwargs):
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

class KeywordUpdate(OnlyYouMixin, generic.CreateView):
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
        keyword.user_id = self.kwargs['pk']
        today = datetime.date.today()
        
        try:
            rank = Rank(keyword = keyword, domain=keyword.domain)
            keyword.save()
            rank.save() 
           
            return redirect('dashboard', pk=self.kwargs['pk'])
        except:
            return redirect('dashboard', pk=self.kwargs['pk'])

# class KeywordDelete(generic.ListView):
#     model = Keyword

#     def post(self, request):
#         keyword_pks = request.POST.getlist('delete')  # <input type="checkbox" name="delete"のnameに対応
#         Keyword.objects.filter(pk__in=keyword_pks).delete()
#         return redirect('dashboard', pk=self.kwargs['pk'])

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    # try:

    load_template = request.path.split('/')[-1]

    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))
    context['segment'] = load_template
    html_template = loader.get_template('home/' + load_template)
    return HttpResponse(html_template.render(context, request))

    # except template.TemplateDoesNotExist:

    #     html_template = loader.get_template('home/page-404.html')
    #     return HttpResponse(html_template.render(context, request))

    # except:
    #     html_template = loader.get_template('home/page-500.html')
    #     return HttpResponse(html_template.render(context, request))
