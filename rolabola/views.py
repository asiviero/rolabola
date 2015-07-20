from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from rolabola.models import *
from rolabola.forms import SearchForm
from django.db.models import Q
import urllib

# Create your views here.
@login_required
def home(request):
    return render(request, "home.html", {
        "search_form" : SearchForm
    })

def login_and_register(request):

    if request.method == 'POST':
        if request.POST.get("form") == "login_form":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return redirect(request.POST.get('next'))
        elif request.POST.get("form") == "user_creation_form":
            form = UserForm(request.POST)
            form_player = PlayerForm(request.POST)
            if form.is_valid() and form_player.is_valid():
                new_user = form.save()
                username = request.POST.get('username')
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
        results = Group.objects.filter(
            Q(name__icontains=request.GET.get("name"))
        )
    return render(request, "search_results.html", {
        "model" : request.GET.get("qtype"),
        "name_query" : urllib.parse.urlencode({"name":request.GET.get("name")}),
        "results" : results
    })

@login_required
def group(request,id):
    group = get_object_or_404(Group, pk=id)
    user_in_group = group.member_list.filter(pk=request.user.player.id).count() != 0 or \
        group.member_pending_list.count() != 0

    #group.member_pending_list.all()
    return render(request, "group.html", {
        "group":group,
        "user_in_group":user_in_group,
        "request_list":group.member_pending_list.all()
    })

@login_required
def group_join(request,id):
    group = get_object_or_404(Group, pk=id)
    request.user.player.join_group(group)
    return redirect(reverse("Group",args=(group.id,)))

@login_required
def group_accept_request(request,group,player):
    group = get_object_or_404(Group, pk=group)
    player = get_object_or_404(Player, pk=player)
    request.user.player.accept_request_group(group,player)
    return redirect(reverse("Group",args=(group.id,)))

@login_required
def group_create(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            print(request.user.player)
            group = group_form.save(commit = False)
            group = request.user.player.create_group(name=group.name,public=group.public)
            return redirect(reverse("Group", args=(group.id,)))
    return render(request, "group_create.html", {
        "group_form":GroupForm
    })
