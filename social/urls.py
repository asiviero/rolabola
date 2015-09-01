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
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.login_and_register),
    url(r'^logout/$', auth_views.logout_then_login),
    url(r'^search/*$', views.search, name="search"),
    url(r'^group/(\d+)/$', views.group, name="Group"),
    url(r'^group/create$', views.group_create, name="group-create"),
    url(r'^group/(\d+)/join$', views.group_join, name="group-join"),
    url(r'^group/(\d+)/private$', views.group_make_private, name="group-make-private"),
    url(r'^group/(\d+)/automatic_confirmation$', views.toggle_automatic_confirmation, name="toggle-automatic-confirmation"),
    url(r'^group/(\d+)/accept/(\d+)$', views.group_accept_request, name="group-accept-request"),
    url(r'^group/(\d+)/reject/(\d+)$', views.group_reject_request, name="group-reject-request"),
    url(r'^group/(\d+)/match$', views.group_match_create, name="group-match-create"),
    url(r'^group/(\d+)/match/(\d+)/$', views.group_match, name="group-match"),
    url(r'^group/(\d+)/match/(\d+)/accept$', views.group_match_accept, name="group-match-accept"),
    url(r'^group/(\d+)/match/(\d+)/reject$', views.group_match_reject, name="group-match-reject"),
    url(r'^calendar/update-weekly/$', views.calendar_update_weekly, name="calendar-update-weekly"),
    url(r'^calendar/update-monthly/$', views.calendar_update_monthly, name="calendar-update-monthly"),
    url(r'^venue/(\d+)/$', views.venue, name="venue"),
    url(r'^venue/create$', views.venue_create, name="venue-create"),
    url(r'^message/(\d+)/delete$', views.message_delete, name="message-delete")

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
