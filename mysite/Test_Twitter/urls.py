from django.conf.urls import url
from Test_Twitter import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^tweet', views.tweet),
    url(r'^search', views.search),
    url(r'^admin', views.admin),
    url(r'^login', views.login),
    url(r'^look/(?P<user_name>\w+)/(?P<post_name>\w+)', views.look),
    url(r'^callback', views.callback),
]
