from django.conf.urls import include, url
from django.contrib import admin
from rolabola import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Examples:
    # url(r'^$', 'social.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.login_and_register),
    url(r'^logout/$', auth_views.logout_then_login),
    url(r'^search/*$', views.search, name="search")
]
