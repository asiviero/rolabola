from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.template import Context, Template, loader
from django.db.models import Count, When, F
from rolabola.models import *
from rolabola.forms import SearchForm
from rolabola.decorators import *
from django_ajax.decorators import ajax
from django_ajax.shortcuts import render_to_json
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
import urllib
import datetime
import dateutil.relativedelta
import json
from django.utils import timezone
from guardian.decorators import permission_required_or_403

# Create your views here.
@login_required
def home(request):
    last_sunday = (datetime.date.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1)))
    next_saturday = last_sunday + datetime.timedelta(days=6)
    dates = [last_sunday + datetime.timedelta(days=x) for x in range(7)]
    match_invitations_in_week = MatchInvitation.objects.filter(
        player__pk = request.user.player.pk,
        match__date__gte=timezone.make_aware(datetime.datetime.combine(last_sunday,datetime.time.min)),
        match__date__lte=timezone.make_aware(datetime.datetime.combine(next_saturday,datetime.time.max))
    )
    match_invitations = {k:[] for k in [x.day for x in dates]}

    match_invitation_template = loader.get_template("match_invitation_calendar.html")
    for match_invitation in match_invitations_in_week:
        match_invitations.get(match_invitation.match.date.day).append(match_invitation_template.render({"match_invitation":match_invitation}))

    return render(request, "home.html", {
        "search_form" : SearchForm,
        "dates": [{"date":x,"label":x.strftime("%a"),"matches":match_invitations.get(x.day)} for x in dates],
        "match_invitations_in_week":match_invitations,
        "membership_requests":request.user.player.get_membership_requests_for_managed_groups()
    })

@login_required
@ajax
def calendar_update_weekly(request):
    base_date = timezone.make_aware(datetime.datetime(int(request.POST.get("year")),int(request.POST.get("month")),int(request.POST.get("day"))))
    base_date += dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
    base_date += datetime.timedelta(days=(1 if request.POST.get("next") != "0" else -1) * 7)
    dates = [base_date + datetime.timedelta(days=x) for x in range(7)]
    response = {
        "year" : base_date.year,
        "month" : base_date.month,
        "day" : base_date.day,
        "inner-fragments" : {}
    }

    match_invitations_in_week = request.user.player.get_match_invitations(start_date=base_date,end_date=base_date+datetime.timedelta(days=7))
    match_invitations = {k:[] for k in [x.day for x in dates]}

    match_invitation_template = loader.get_template("match_invitation_calendar.html")
    for match_invitation in match_invitations_in_week:
        match_invitations.get(match_invitation.match.date.day).append(match_invitation_template.render({"match_invitation":match_invitation}))
    for date_query in dates:
        response["inner-fragments"][".calendar-table.weekly th.%s" % date_query.strftime("%a").lower()] = "%s %s"  % (date_query.strftime("%a"),date_query.strftime("%d"))
        response["inner-fragments"][".calendar-table.weekly td.%s" % date_query.strftime("%a").lower()] = "%s"  % "".join(match_invitations.get(date_query.day))
    return response

@group_membership_required
@login_required
@ajax
def calendar_update_monthly(request):
    group = get_object_or_404(Group, pk=request.POST.get("group"))
    base_date = timezone.make_aware(datetime.datetime(int(request.POST.get("year")),int(request.POST.get("month")),int(request.POST.get("day"))))
    base_date += dateutil.relativedelta.relativedelta(months=(1 if request.POST.get("next") != "0" else -1))

    first_day_of_month = datetime.date(base_date.year,base_date.month,1)
    sunday_before_first_day_of_month = first_day_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
    last_date_of_month = datetime.date(base_date.year,base_date.month,1)+dateutil.relativedelta.relativedelta(months=1)
    next_saturday_after_last_date_of_month = last_date_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(+1))

    days = [(sunday_before_first_day_of_month + datetime.timedelta(days=x)).strftime("%a") for x in range(7)]

    dates = [sunday_before_first_day_of_month + datetime.timedelta(days=x) for x in range(0, (next_saturday_after_last_date_of_month-sunday_before_first_day_of_month).days+1)]
    match_invitations_in_month = request.user.player.get_match_invitations(group=group,
                                                                                                                     start_date=sunday_before_first_day_of_month,
                                                                                                                     end_date=next_saturday_after_last_date_of_month)
    match_templates = {k:[] for k in [x for x in dates]}

    match_invitation_template = loader.get_template("match_invitation_calendar.html")
    for match_invitation in match_invitations_in_month:
        match_templates[match_invitation.match.date.date()].append(match_invitation_template.render({"match_invitation":match_invitation}))
    dates = [{"date":x,"match_list":match_templates[x]} for x in dates]
    weeks = [dates[x:x+7] for x in range(0, len(dates), 7)]

    calendar_template = loader.get_template("calendar/monthly_calendar.html")
    calendar_view = calendar_template.render({"days_label":days,"weeks":weeks,"today":base_date})

    return {
        "year" : base_date.year,
        "month" : base_date.month,
        "day" : base_date.day,
        "inner-fragments": {
            "#calendar-monthly-view .calendar-table" : calendar_view,
            "#calendar-monthly-view .month-name" : base_date.strftime("%B")
        }
    }

@group_membership_required
@login_required
@ajax
def toggle_automatic_confirmation(request,group):
    group = get_object_or_404(Group,pk=group)
    automatic_confirmation = request.user.player.toggle_automatic_confirmation_in_group(group=group)
    response = {
        "automatic_confirmation" :  automatic_confirmation
    }
    return response

def login_and_register(request):

    if request.method == 'POST':
        if request.POST.get("form") == "login_form":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    if request.POST.get('next') :
                        return redirect(request.POST.get('next'))
                    return redirect(reverse("home"))
        elif request.POST.get("form") == "user_creation_form":
            form = UserForm(request.POST)
            form_player = PlayerForm(request.POST)
            if form.is_valid() and form_player.is_valid():
                new_user = form.save()
                username = request.POST.get('email')
                password = request.POST.get('password1')

                # Player
                new_player = form_player.save(commit = False)
                new_player.user = new_user
                new_player.save()

                user = authenticate(username=username,password=password)
                login(request,user)
                return redirect(request.POST.get('next'))

    else:
        pass
    return render(request,'login_register.html', {
        "login_form" : AuthenticationForm,
        "user_creation_form" : UserForm,
        "player_form" : PlayerForm,
        "next" : request.GET.get("next")
    })

def search(request):
    results = []
    if request.GET.get("qtype") == "User" or request.GET.get("qtype") == "":
        results = User.objects.filter(
            Q(first_name__icontains=request.GET.get("name")) |
            Q(last_name__icontains=request.GET.get("name")) |
            Q(player__nickname__icontains=request.GET.get("name"))
        )
    elif request.GET.get("qtype") == "Group":

        if not request.user.is_anonymous():
            friend_list = [x.pk for x in request.user.player.friend_list.all()]
            if len(friend_list) :
                results = Group.objects.filter(
                    Q(name__icontains=request.GET.get("name"))
                ).annotate(member_list_count=Count(Q(membership__member__in=friend_list),distinct=True)).order_by("-member_list_count")
            else :
                results = Group.objects.filter(
                    Q(name__icontains=request.GET.get("name"))
                )
        else :
            results = Group.objects.filter(
                Q(name__icontains=request.GET.get("name"))
            )

        group_result_list_template = loader.get_template("search/search_result_group.html")
        results = [group_result_list_template.render({
            "group":x,
            "member":False if request.user.is_anonymous() else x.member_list.filter(pk=request.user.player.pk).exists() ,
            "membership_requested":False if request.user.is_anonymous() else x.member_pending_list.filter(pk=request.user.player.pk).exists(),
            "friends_in_group":[] if request.user.is_anonymous() else x.get_friends_from_user(request.user.player)
        }) for x in results]

    return render(request, "search_results.html", {
        "model" : request.GET.get("qtype"),
        "name_query" : urllib.parse.urlencode({"name":request.GET.get("name")}),
        "results" : results
    })

@login_required
def group(request,group):
    group = get_object_or_404(Group, pk=group)

    user_in_group = group.member_list.filter(pk=request.user.player.id).count() != 0
    user_requested_membership = group.member_pending_list.filter(pk=request.user.player.id).count() != 0
    is_admin = request.user.player in group.member_list.filter(membership__role=Membership.GROUP_ADMIN)
    try:
        automatic_confirmation = Membership.objects.get(member__pk=request.user.player.id,group__pk=group.pk).automatic_confirmation
    except:
        automatic_confirmation = False
    #days = [datetime.date(2001, 1, i).strftime('%a') for i in range(1,8)]


    today = datetime.date.today()
    first_day_of_month = datetime.date(today.year,today.month,1)
    sunday_before_first_day_of_month = first_day_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
    last_date_of_month = datetime.date(today.year,today.month,1)+dateutil.relativedelta.relativedelta(months=1)
    next_saturday_after_last_date_of_month = last_date_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(+1))


    days = [(sunday_before_first_day_of_month + datetime.timedelta(days=x)).strftime("%a") for x in range(7)]

    dates = [sunday_before_first_day_of_month + datetime.timedelta(days=x) for x in range(0, (next_saturday_after_last_date_of_month-sunday_before_first_day_of_month).days+1)]
    match_invitations_in_month = request.user.player.get_match_invitations(group=group,
                                                                                                                     start_date=sunday_before_first_day_of_month,
                                                                                                                     end_date=next_saturday_after_last_date_of_month)
    match_templates = {k:[] for k in [x for x in dates]}

    match_invitation_template = loader.get_template("match_invitation_calendar.html")
    for match_invitation in match_invitations_in_month:
        match_templates[match_invitation.match.date.date()].append(match_invitation_template.render({"match_invitation":match_invitation}))
    dates = [{"date":x,"match_list":match_templates[x]} for x in dates]
    weeks = [dates[x:x+7] for x in range(0, len(dates), 7)]

    calendar_template = loader.get_template("calendar/monthly_calendar.html")

    calendar_view = calendar_template.render({"days_label":days,"weeks":weeks,"today":today})

    message_list_template = loader.get_template("message/message.html")
    rendered_messages = [message_list_template.render({"message":message,"is_admin":is_admin,"player":request.user.player}) for message in group.get_messages()]
    # message_list_template.render({"message":self})

    return render(request, "group.html", {
        "group":group,
        "user_in_group":user_in_group,
        "user_requested_membership":user_requested_membership,
        "request_list":group.member_pending_list.all(),
        "is_admin":is_admin,
        "calendar_view":calendar_view,
        "automatic_confirmation":automatic_confirmation,
        "message_form":MessageForm,
        "messages":rendered_messages
    })

@login_required
@ajax
def group_join(request,group):
    group = get_object_or_404(Group, pk=group)
    membership_or_request = request.user.player.join_group(group)
    is_membership = isinstance(membership_or_request,Membership)
    response = {
        "membership" : str(is_membership).lower()
    }
    if is_membership :
        response["append-fragments"] = {
            "#member-list ul" : "<li>%s %s (%s)</li>" % (request.user.first_name,request.user.last_name,request.user.player.nickname)
        }
    else:
        if not "search" in request.META.get("HTTP_REFERER"):
            response["replace_string"] = "membership requested"
    # print(response)
    return response

@group_admin_required
@login_required
@ajax
def group_make_private(request,group):
    group = get_object_or_404(Group, pk=group)
    group.public = not group.public
    group.save()
    response = {
        "message" : "Group status changed to %s" % ("Public" if group.public else "Private")
    }
    return response

@group_admin_required
@login_required
@ajax
def group_accept_request(request,group,player):
    group = get_object_or_404(Group, pk=group)
    player = get_object_or_404(Player, pk=player)
    request.user.player.accept_request_group(group,player)
    response = {
        "message" : "%s Accepted into group %s" % (player,group.name)
    }
    if "group/%s" % group.pk in request.META.get("HTTP_REFERER"):
        response["append-fragments"] = {
            "#member-list ul" : "<li>%s %s (%s)</li>" % (player.user.first_name,player.user.last_name,player.nickname)
        }
    return response

@group_admin_required
@login_required
@ajax
def group_reject_request(request,group,player):
    group = get_object_or_404(Group, pk=group)
    player = get_object_or_404(Player, pk=player)
    request.user.player.reject_request_group(group,player)
    response = JsonResponse({
        "message" : "%s rejected into group %s" % (player,group.name)
    })
    response.status_code = 200
    return response

@login_required
def group_create(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST, request.FILES)
        if group_form.is_valid():
            group = group_form.save(commit = False)
            group = request.user.player.create_group(name=group.name,public=group.public,picture=group.picture)
            return redirect(reverse("Group", args=(group.id,)))
    return render(request, "group_create.html", {
        "group_form":GroupForm
    })

@login_required
def group_match_create(request,group):
    if request.method == 'POST':
        group_match_create_form = MatchForm(request.POST)
        if group_match_create_form.is_valid():
            today = datetime.datetime.now()
            if group_match_create_form.cleaned_data["until_end_of_year"]:
                until = timezone.make_aware(datetime.datetime(today.year,12,31))
            elif group_match_create_form.cleaned_data["until_end_of_month"]:
                until = timezone.make_aware(datetime.datetime(today.year,today.month,1)+dateutil.relativedelta.relativedelta(months=1,days=-1))
            else:
                until = None
            match = request.user.player.schedule_match(
                group=get_object_or_404(Group,pk=group),
                date=group_match_create_form.cleaned_data["date"],
                max_participants=group_match_create_form.cleaned_data["max_participants"],
                min_participants=group_match_create_form.cleaned_data["min_participants"],
                price=group_match_create_form.cleaned_data["price"],
                until=until
            )
            return redirect(reverse("group-match", args=(match.group.id,match.id,)))
    return render(request, "group_match_create.html", {
        "group_match_create_form":MatchForm,
    })

@login_required
def group_match(request,group,match):
    group=get_object_or_404(Group,pk=group)
    match=get_object_or_404(Match,pk=match)
    context = {
        "group":group,
        "match": match,
        "user_is_admin":request.user.player in group.member_list.filter(membership__role=Membership.GROUP_ADMIN),
    }

    if request.user.player in match.get_unanswered_list():
        context["header"] = request.user.player
        context["unaswered"] = match.get_unanswered_list().exclude(pk=request.user.player.pk)
    else:
        context["header"] = None
        context["unaswered"] = match.get_unanswered_list()

    match_confirmed_list_template = loader.get_template("match/match_confirmed_list.html")
    context["confirmed_list"] = match_confirmed_list_template.render(context)

    return render(request, "group_match.html", context)

@login_required
@ajax
def group_match_accept(request,group,match):
    group=get_object_or_404(Group,pk=group)
    match=get_object_or_404(Match,pk=match)

    if request.GET.get("u") is not None:
        if request.user.player in group.member_list.filter(membership__role=Membership.GROUP_ADMIN):
            player = get_object_or_404(Player,pk=request.GET.get("u"))
        else:
            return {}
    else:
        player = request.user.player

    print(player.pk)
    player.accept_match_invitation(match=match)
    match_invitation_template = loader.get_template("match_invitation_calendar.html")

    match_confirmed_list_template = loader.get_template("match/match_confirmed_list.html")
    context = {
        "group":group,
        "match": match,
    }

    if request.user.player in match.get_unanswered_list():
        context["header"] = request.user.player
        context["unaswered"] = match.get_unanswered_list().exclude(pk=request.user.player.pk)
    else:
        context["header"] = None
        context["unaswered"] = match.get_unanswered_list()

    response = {
        "inner-fragments" : {
            ".match-invitation[data-match='%s']" % match.pk : match_invitation_template.render({"match_invitation":MatchInvitation.objects.get(player__pk=request.user.player.pk,match__pk=match.pk)}),
            ".confirmed-list-wrapper" : match_confirmed_list_template.render(context)
        }
    }
    return response

@login_required
@ajax
def group_match_reject(request,group,match):
    group=get_object_or_404(Group,pk=group)
    match=get_object_or_404(Match,pk=match)

    if request.GET.get("u") is not None:
        if request.user.player in group.member_list.filter(membership__role=Membership.GROUP_ADMIN):
            player = get_object_or_404(Player,pk=request.GET.get("u"))
        else:
            return {}
    else:
        player = request.user.player

    player.refuse_match_invitation(match=match)
    match_invitation_template = loader.get_template("match_invitation_calendar.html")

    match_confirmed_list_template = loader.get_template("match/match_confirmed_list.html")
    context = {
        "group":group,
        "match": match,
    }

    if request.user.player in match.get_unanswered_list():
        context["header"] = request.user.player
        context["unaswered"] = match.get_unanswered_list().exclude(pk=request.user.player.pk)
    else:
        context["header"] = None
        context["unaswered"] = match.get_unanswered_list()

    response = {
        "inner-fragments" : {
            ".match-invitation[data-match='%s']" % match.pk : match_invitation_template.render({"match_invitation":MatchInvitation.objects.get(player__pk=request.user.player.pk,match__pk=match.pk)}),
            ".confirmed-list-wrapper" : match_confirmed_list_template.render(context)
        }
    }

    return response

@login_required
@group_membership_required
@ajax
def message_send(request,group):
    group = get_object_or_404(Group,pk=group)
    message = request.user.player.send_message_group(group=group,message=request.POST.get("message"))
    if not message is None:
        message_list_template = loader.get_template("message/message.html")
        return {
            "prepend-fragments" : {
                "#message-wall" : message_list_template.render({"message":message})
            }
        }
    else:
        return HttpResponseServerError()

@login_required
def venue(request,venue):
    venue = get_object_or_404(Venue,pk=venue)
    return render(request, "venue/venue.html", {
        "venue":venue,
    })
    pass

@login_required
def venue_create(request):
    if request.method == 'POST':
        venue_create_form = VenueForm(request.POST)
        if venue_create_form.is_valid():
            venue = Venue.objects.create(
                quadra=venue_create_form.cleaned_data["quadra"],
                address=venue_create_form.cleaned_data["address"],
                location=venue_create_form.cleaned_data["location"],
            )
            if(request.is_ajax()) :
                response = {"id":venue.pk, "append-fragments" : {"#id_venue" : "<option value='%s'>%s</option>" % (venue.pk,venue.quadra)}}
                return render_to_json(response)
            return redirect(reverse("venue", args=(venue.pk,)))
    return render(request, "venue/venue_create.html", {
        "venue_form":VenueForm,
    })

def turn_message_arg_into_message_kwarg(view_func):
    def _wrapped_view_func(player, *args, **kwargs):
        kwargs["message"] = args[0]
        args = {}
        return view_func(player, *args, **kwargs)
    return _wrapped_view_func


@turn_message_arg_into_message_kwarg
@permission_required_or_403("delete_message",(Message,"pk","message"))
@ajax
def message_delete(request,message):
    message = get_object_or_404(Message,pk=message)
    pk = message.pk
    group = message.group
    message.delete()
    return {
        "fragments" : {
            ".message-wrapper[data-message=%s]" % pk : ""
        }
    }
