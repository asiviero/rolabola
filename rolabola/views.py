from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from social_list.models import Player, PlayerForm, UserForm, Group
from social_list.forms import SearchForm
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
