from django.http import JsonResponse


def getRoute(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/room/:id'
    ]
    return JsonResponse(routes, safe=False) # safe=False allows the routes list to be turned to json.