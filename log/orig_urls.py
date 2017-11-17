from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'log'
urlpatterns = [
    url(r'^login/$', views.login_view, name='login_url'),
    url(r'^signup/$', views.signup_view, name='signup_url'),
    url(r'^logout/$', views.logout_view, name='logout_url'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate_view, name='activate_url'),
]
