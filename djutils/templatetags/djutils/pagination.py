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
    request = context['request']
    qs = list()
    for k, v in request.GET.items():
        if k == 'page':
            continue
        qs.append(u'%s=%s' % (k, v))
    paginator_url = "%s?%s" % (request.path, '&'.join(qs))
    if qs: paginator_url += '&'
    page = context.get('page', 1)
    pages = context.get('pages', 1)
    page_numbers = [n for n in range(page - adjacent_pages, \
                    page + adjacent_pages + 1) if n > 0 and \
                    n <= pages]
    return {
        'paginator_url': paginator_url,
        'is_paginated': context['is_paginated'],
        'hits': context.get('hits'),
        'results_per_page': context.get('results_per_page'),
        'page': page,
        'pages': pages,
        'page_numbers': page_numbers,
        'next': context.get('next'),
        'previous': context.get('previous'),
        'has_next': context.get('has_next'),
        'has_previous': context.get('has_previous'),
        'show_first': 1 not in page_numbers,
        'show_last': pages not in page_numbers,
    }

register.inclusion_tag('paginator.html', takes_context=True)(paginator)
