from urlparse import urlparse
from django import template

register = template.Library()

def paginator(context, adjacent_pages=2):
    """
    Based on http://www.djangosnippets.org/snippets/73/

    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    You must add 'django.core.context_processors.request' to your
    TEMPLATE_CONTEXT_PROCESSORS setting.
    """
    request = context.get('request')
    page_numbers = [n for n in range(context['page'] - adjacent_pages, \
                    context['page'] + adjacent_pages + 1) if n > 0 and \
                    n <= context['pages']]
    request_url, paginator_url = '', ''
    if request: request_url = request.get_full_path()
    querystring = urlparse(request_url).query
    if querystring == '': paginator_url += '?'
    params = dict([part.split('=') for part in querystring.split('&')])
    if 'page' in params: del params['page']
    paginator_url = request.path + '&'.join(['%s=%s' % (k, v) for k, v \
                                             in params.items()])
    return {
        'paginator_url': paginator_url,
        'is_paginated': context['is_paginated'],
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
    }

register.inclusion_tag('paginator.html', takes_context=True)(paginator)
