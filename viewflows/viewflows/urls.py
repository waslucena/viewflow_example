"""viewflows URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin
from adminplus.sites import AdminSitePlus
from viewflow import views as viewflow
from .flows.flows import HelloWorldFlow, PublishPollFlow

admin.site = AdminSitePlus()
admin.autodiscover()

flow_classes = [HelloWorldFlow, PublishPollFlow]

urlpatterns = [
    url(r'^admin/helloworld',
        include([
            HelloWorldFlow.instance.urls,
            # url('^$', viewflow.ProcessListView.as_view(), name='index'),
            # url('^tasks/$', viewflow.TaskListView.as_view(), name='tasks'),
            # url('^queue/$', viewflow.QueueListView.as_view(), name='queue'),
            url('^details/(?P<process_pk>\d+)/$',
                viewflow.ProcessDetailView.as_view(), name='details')
            ],
            namespace=HelloWorldFlow.instance.namespace),
        {'flow_cls': HelloWorldFlow}),
    url(r'^admin/publispoll',
        include([
            PublishPollFlow.instance.urls,
            # url('^$', viewflow.ProcessListView.as_view(), name='index'),
            # url('^tasks/$', viewflow.TaskListView.as_view(), name='tasks'),
            # url('^queue/$', viewflow.QueueListView.as_view(), name='queue'),
            url('^details/(?P<process_pk>\d+)/$',
                viewflow.ProcessDetailView.as_view(), name='details')
            ],
            namespace=PublishPollFlow.instance.namespace),
        {'flow_cls': PublishPollFlow}),
    url(r'^admin/', include(admin.site.urls)),
]


