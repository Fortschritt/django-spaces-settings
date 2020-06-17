# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms.fields import BooleanField
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic.edit import DeleteView

from actstream.signals import action as actstream_action

from collab.decorators import manager_required
from collab.mixins import ManagerRequiredMixin
from spaces.models import Space, SpacePluginRegistry

def base_extra_context(request):
    extra_context = {}
    extra_context['plugin_selected'] = 'settings'
    return extra_context

@manager_required
def settings(request):
    """
    The general settings page for a Space.
    """
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({'success': True, 'space': request.SPACE.slug}), status=403)
    extra_context = base_extra_context(request)
    return render(request,'spaces_settings/settings.html',extra_context) 

@manager_required
def toggle_plugin(request):
    """
    activate or deactivate a plugin for this Space
    """
    space = request.SPACE
    if request.method == "POST":
        plugin_name = request.POST['plugin_name'] if 'plugin_name' in \
                    request.POST.keys() else None
        active = request.POST['plugin_active'] if 'plugin_active' in \
                    request.POST.keys() else None
        active = BooleanField(required=False).clean(active)
        if plugin_name and active in (True, False):
            plugin = SpacePluginRegistry().get_plugin(plugin_name)
            model = SpacePluginRegistry().get_instance(plugin_name, space)
            model.active = active
            model.save()
            from django.utils.translation import ugettext_lazy
            if active:
                print(plugin.title, type(plugin.title), dir(plugin.title))
                from django.utils.encoding import force_text
                msg = _("Plugin \"%(title)s\" activated.") % \
                    {'title':plugin.title}
            else:
                msg = _("Plugin \"%(title)s\" deactivated.") % \
                    {'title':plugin.title}
            actstream_action.send(
                sender=request.user,
                verb=_("has been modified"),
                action_object=space
            )
            messages.success(request, msg)
        else:
            messages.error(request, \
                _("You have to provide both a plugin name and new state."))
    else:
        messages.error(request, _("No form data found"))
    return redirect('spaces_settings:settings')

class DeleteSpace(ManagerRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Delete a Space.
    """
    model = Space
    pk_url_kwarg = 'space_pk'
    success_message = _("Space was deleted successfully")
    success_url = reverse_lazy('collab_user_views:dashboard')
    template_name = 'spaces_settings/space_confirm_delete.html'
