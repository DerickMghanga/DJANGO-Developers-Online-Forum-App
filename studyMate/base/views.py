from django.shortcuts import render, redirect
from django.db.models import Q # enables use of AND('&') or OR('|') in db queries
from django.contrib.auth.models import User # built-in db table Django Framework
from django.contrib import messages  # django flash messages
from django.contrib.auth.decorators import login_required  # restrict specific pages
from django.contrib.auth import authenticate, login, logout  # in-built in Django
from django.http import HttpResponse
from .models import Room, Topic
from .forms import RoomForm

# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets Learn Python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Front-End Developers'},
# ]


# User Login functionality in Django from scratch
def loginPage(request):
    #redirect user to home page if already logged in(can't visit login page)
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # check if user exists in users table
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist!")
        # authentication in Django >> check if the user credentials are correct
        user = authenticate(request, username=username, password=password) 

        if user is not None:
            login(request, user)  # adds session to the DB and returns session(token) to client
            return redirect('home')
        else:
             messages.error(request, "Username OR Password is Incorrect!")

    context = {}
    return render(request, 'base/login_register.html', context)


# Django Log-Out
def logOutUser(request):
    logout(request)  #delete token in client
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' # query value from the url after selecting a topic(Browse Topics)
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)) #filter upwards from topic attribute to Topic Model. topic name atleast contains whats in the query
    topics = Topic.objects.all()
    rooms_count = rooms.count() #gets length of a queryset also you can use>> len(rooms) basic python

    context = {'rooms': rooms, 'topics': topics, 'rooms_count':rooms_count}
    return render(request, 'base/home.html', context)


def room(request, pk):  #Dynamic route in Python
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)


@login_required(login_url='/login') # redirects to user if not logged in
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        #print(request.POST)
        form = RoomForm(request.POST) #process the data submitted in the form
        if form.is_valid():
            form.save() #saves the data in the db
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #pre-fills the initial data before editing
    # authentication >> only owners of the room can update the room
    if request.user != room.host:
        return HttpResponse('You are not allowed to Update this room!!')
    #update the form
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    # authentication >> only owners of the room can delete the room
    if request.user != room.host:
        return HttpResponse('You are not allowed to Delete this room!!')
    #delete the room after user accepts to delete
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})