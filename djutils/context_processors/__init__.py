from django.conf import settings

def default(request):
    return {
        'sort': request.GET.get('s', ''),
        'query': request.GET.get('q', ''),
        'host': request.get_host(),
        'full_path': request.get_full_path(),
        'is_secure': request.is_secure(),
        'is_ajax': request.is_ajax(),
    }
