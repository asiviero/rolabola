from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from rolabola.models import *

def group_admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        group = get_object_or_404(Group, pk=args[0])
        if Membership.objects.filter(member__pk=request.user.player.pk,group__pk=group.pk,role=Membership.GROUP_ADMIN).count():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view_func

def group_membership_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        group_pk = request.POST.get("group") if request.POST.get("group") is not None else args[0]
        group = get_object_or_404(Group, pk=group_pk)
        if Membership.objects.filter(member__pk=request.user.player.pk,group__pk=group.pk).count():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view_func
