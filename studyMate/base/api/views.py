from rest_framework.decorators import api_view  #decorator
from rest_framework.response import Response

from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])  # http methods allowed to access this view
def getRoute(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/room/:id'
    ]
    return Response(routes) # return info about all api routes fro the users

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()  # returns Python objects that are not serializable
    serializer = RoomSerializer(rooms, many=True)
    #print(serializer.data)
    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)  # returns Python objects that are not serializable
    serializer = RoomSerializer(room, many=False)
    #print(serializer.data)
    return Response(serializer.data)