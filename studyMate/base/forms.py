from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User #built-in db table Django Framework


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'  #creates form fields based on attributes in 'Room' model
        exclude = ['host', 'participants']  # exclude a field in the form


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']