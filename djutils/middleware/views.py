# http://www.djangosnippets.org/snippets/1153/

class ActiveViewMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Records the view function used on this request and its *args and **kwargs.
        Needed by {% ifactive %} to determine if a particular view is currently active.
        """
        request._view_func = view_func
        request._view_args = list(view_args)
        request._view_kwargs = view_kwargs
