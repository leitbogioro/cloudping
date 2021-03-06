# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.db.models import Count
from django.contrib.auth.models import Group

from .models import Service, Company, Region
from apps.promotion.models import Promotion


class BaseMixin(object):
    @classmethod
    def get_companies(cls):
        rs = Service.objects.filter(status=0).values('company').annotate(total=Count('company')).order_by('-total')
        companies = []
        for r in rs:
            company = Company.objects.get(pk=r['company'])
            company.region_count = r['total']
            companies.append(company)
        return sorted(companies, key=lambda o: o.order)

    @classmethod
    def navigation_count(cls):
        group = Group.objects.first()
        return group and group.name or "14"


class IndexView(BaseMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        companies = self.get_companies()
        context['companies'] = companies
        context['company'] = 'all'
        context['rows'] = self.get_rows(companies)
        context['description'] = u'主流云平台地域分布及其延迟'
        context['navigation_count'] = self.navigation_count()
        return context

    @classmethod
    def get_rows(cls, companies):
        locations = Region.objects.order_by('order')
        rows = []
        for location in locations:
            row = [location]
            for c in companies:
                row.append(bool(Service.objects.filter(company=c, region=location)))
            rows.append(row)
        return rows


class CompanyView(BaseMixin, TemplateView):
    template_name = "company.html"

    @classmethod
    def to_matrix(cls, l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)
        companies = self.get_companies()
        context['companies'] = companies
        context['company'] = company = Company.objects.filter(code=kwargs['code']).first()
        context['ss'] = Service.objects.filter(company=context['company'], status=0).order_by('region__order')
        context['description'] = company.description
        context['navigation_count'] = self.navigation_count()
        promotions = Promotion.objects.filter(company=company).order_by('order')
        context['promotions'] = self.to_matrix(promotions, 2)
        return context
