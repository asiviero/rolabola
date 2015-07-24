from django.conf.urls import include, url
from django.contrib import admin
from rolabola import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Examples:
    # url(r'^$', 'social.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.login_and_register),
    url(r'^logout/$', auth_views.logout_then_login),
    url(r'^search/*$', views.search, name="search"),
    url(r'^group/(\d+)/$', views.group, name="Group"),
    url(r'^group/create$', views.group_create, name="group-create"),
    url(r'^group/(\d+)/join$', views.group_join, name="group-join"),
    url(r'^group/(\d+)/accept/(\d+)$', views.group_accept_request, name="group-accept-request"),
    url(r'^group/(\d+)/match$', views.group_match_create, name="group-match-create"),
    url(r'^group/(\d+)/match/(\d+)/$', views.group_match, name="group-match"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
