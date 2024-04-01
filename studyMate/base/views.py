from django.shortcuts import render, redirect
from django.db.models import Q # enables use of AND('&') or OR('|') in db queries
from django.contrib.auth.models import User # built-in db table Django Framework
from django.contrib import messages  # django flash messages
from django.contrib.auth.decorators import login_required  # restrict specific pages
from django.contrib.auth import authenticate, login, logout  # in-built in Django
from django.contrib.auth.forms import UserCreationForm #in-built to help create new Users
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets Learn Python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Front-End Developers'},
# ]


# User Login functionality in Django from scratch
def loginPage(request):
    page = 'login'
    #redirect user to home page if already logged in(can't visit login page)
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()  # get the details and set to lowercase
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

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


# Django Log-Out
def logOutUser(request):
    logout(request)  #delete token in client
    return redirect('home')

# create user account(sign up)
def registerPage(request):
    form = UserCreationForm()
    #process data recieved from the form
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # access user details before saving to DB
            user.username == user.username.lower() # set user's username to lowercase
            user.save()
            login(request, user) # automatically logs in the user after registration
            return redirect('home')
        else:
            messages.error(request, 'An Error Occured during Registration!')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' # query value from the url after selecting a topic(Browse Topics)
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)) #filter upwards from topic attribute to Topic Model. topic name atleast contains whats in the query
    topics = Topic.objects.all()
    rooms_count = rooms.count() #gets length of a queryset also you can use>> len(rooms) basic python
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))  # Recent activity  section >> filter all messages according to topic name

    context = {'rooms': rooms, 'topics': topics, 'rooms_count':rooms_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):  #Dynamic route in Python
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()  # gets all messages related to this room
    participants = room.participants.all()  # get all room participants
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user) #add the user to participants of the room
        return redirect('room', pk=room.id) #redirect to the dynamic room page(reload page)

    context = {'room': room, 'room_messages': room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)

# profile page of a user
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()  # fetch all rooms related to the user
    room_messages = user.message_set.all()  # fetch all messages related to the user
    topics = Topic.objects.all()  # all topics
    context = {'user': user, 'rooms':rooms, 'topics':topics, 'room_messages':room_messages}
    return render(request, 'base/profile.html', context)


@login_required(login_url='/login') # redirects to user to log in if not logged in
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        #print(request.POST)
        topic_name = request.POST.get('topic') # get the topic value from input >> name='topic'
        topic, created = Topic.objects.get_or_create(name=topic_name) # get a topic or create it incase it doesn't exist
        Room.objects.create(
            host = request.user,
            topic=topic,
            name= request.POST.get('name'),
            description= request.POST.get('description')
        )
        return redirect('home')
        #form = RoomForm(request.POST) #process the data submitted in the form
        # if form.is_valid():
        #     room = form.save(commit=False) # get room data before saving to the db
        #     room.host = request.user  # logged in user as host of the created room
        #     room.save()
            #return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    form = RoomForm(instance=room) #pre-fills the initial data before editing
    # authentication >> only owners of the room can update the room
    if request.user != room.host:
        return HttpResponse('You are not allowed to Update this room!')
    #update the form
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic') # get the topic value from input >> name='topic'
        topic, created = Topic.objects.get_or_create(name=topic_name) # get a topic or create it incase it doesn't exist
        room.name = request.POST.get('name')
        room.topic = topic  # inace a new topic is edited by the user
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')
    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    # authentication >> only owners of the room can delete the room
    if request.user != room.host:
        return HttpResponse('You are not allowed to Delete this room!')
    #delete the room after user accepts to delete
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    # authentication >> only owners of the message can delete the message
    if request.user != message.user:
        return HttpResponse('You are not allowed to Delete this message!')
    #delete the message after user accepts to delete
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='/login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)   # after updating take user back to their profile
    return render(request, 'base/update-user.html', {'form':form})


def topicsMobilePage(request):
    return render(request, 'base/topics.html', {})