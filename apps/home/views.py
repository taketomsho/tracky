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


from .models import Keyword, Domain
from .forms import RegisterDomainForm, RegisterKeywordForm


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser



class DomainListView(OnlyYouMixin, ListView):

    def get_queryset(self):
        return Domain.objects.filter(user=self.kwargs['pk'])
    
    template_name = 'home/domain_list.html'
    


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
            return redirect('domain_list', pk=self.kwargs['pk'])
        except:
            return redirect('domain_list', pk=self.kwargs['pk'])

        

class KeywordListView(OnlyYouMixin, ListView):
    def get_queryset(self):
        domain = Domain.objects.filter(user=self.kwargs['pk'])
        return Keyword.objects.filter(domain__in=domain)
    # model = Keyword
    template_name = 'home/keyword_list.html'


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
        try:
            keyword.save()
            return redirect('keyword_list', pk=self.kwargs['pk'])
        except:
            return redirect('keyword_list', pk=self.kwargs['pk'])


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
