from django.core.cache import cache

def cacheable(cache_key, timeout=3600):
    """taken from http://www.djangosnippets.org/snippets/1130/"""
    def paramed_decorator(func):
        def decorated(self):
            key = cache_key % self.__dict__
            res = cache.get(key)
            if res == None:
                res = func(self)
                cache.set(key, res, timeout)
            return res
        decorated.__doc__ = func.__doc__
        decorated.__dict__ = func.__dict__
        return decorated 
    return paramed_decorator

def stales_cache(cache_key):
    """taken from http://www.djangosnippets.org/snippets/1131/"""
    def paramed_decorator(func):
        def decorated(self, *args, **kw):
            key = cache_key % self.__dict__
            cache.delete(key)
            return func(self, *args, **kw)
        decorated.__doc__ = func.__doc__
        decorated.__dict__ = func.__dict__
        return decorated
    return paramed_decorator
