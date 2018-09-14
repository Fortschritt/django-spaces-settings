from django.conf.urls import url
from spaces.urls import space_patterns

from . import views

app_name = 'spaces_settings'
urlpatterns = space_patterns(
    url(r'^settings$', views.settings, name='settings'),
    url(r'^toggle_plugin$', views.toggle_plugin, name='toggle_plugin'),
    url(r'^(?P<space_pk>\d+)/delete_space$', views.DeleteSpace.as_view(), name='delete'),
)
