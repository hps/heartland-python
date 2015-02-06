from django.conf.urls import patterns, url

from ssexample import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^charge/$', views.charge, name='charge'),
)
