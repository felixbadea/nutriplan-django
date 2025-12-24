from django.http import Http404

def current_restaurant(request):
    if hasattr(request, 'current_restaurant'):
        return {'restaurant': request.current_restaurant}
    return {'restaurant': None}