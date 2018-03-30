"""riskserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

import query.views
import testapp.views
import trainapp.views

urlpatterns = [
    url(r'^train/', trainapp.views.register),
    url(r'^test/', testapp.views.register),
    url(r'^query/', query.views.query),
    url(r'^manual_fix/', query.views.manual_fix),
    url(r'^sandeep', trainapp.views.sandeep),
    url(r'^django-rq/', include('django_rq.urls')),
]
