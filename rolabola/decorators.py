from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from rolabola.models import *

def group_admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        group = get_object_or_404(Group, pk=args[0])
        if Membership.objects.filter(member__pk=request.user.pk,group__pk=group.pk,role=Membership.GROUP_ADMIN).count():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view_func
