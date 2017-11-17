from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'log'
urlpatterns = [
    url(r'^login/$', views.login_view, name='login_url'),
    url(r'^logout/$', views.logout_view, name='logout_url'),
]
