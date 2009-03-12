from django import template
from django.conf import settings
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.utils.translation import gettext
from django.core.urlresolvers import get_callable, RegexURLResolver, get_resolver
from django.template import loader, Node, NodeList, TextNode, TemplateSyntaxError, Library, resolve_variable

register = template.Library()

# Based on http://www.djangosnippets.org/snippets/347/

class SimpleMenu(object):
    """
    Stores a tree-like menu hierarchy, and renders it up to a chosen item
    on request.
    """

    def __init__(self, menulist):
        """
        Initializes the class.
        
        The menulist argument is a dictionary of menus. Each key is the menu
        label; the corresponding value is a list of (item_label, urlname)
        pairs.  The 'urlname' is then looked up in the URL configuration in
        order to correctly render the matching link. (See example below.)

        Example MENU_ITEMS setting::

            MENU_ITEMS = {
                'root': (
                    (_('Venues'), 'venue_menu'), 
                    (_('My account'), 'account_menu')
                ),
                'venue_menu': (
                    (_('Browse'), 'venue_browse'), 
                    (_('New venue'), 'eatout-add-venue'),
                ),
            }
        """
        self.menus = menulist

    def render(self, menu_name, depth=0, active=None):
        """
        The render() method returns a HTML string suitable for use as a
        menu bar on a given page.
        
        menu_name: the label of a menu, as specified at class initialization.
        
        depth (kw): an integer specifying how far into the tree this is being
        rendered.  Usually the render() method takes care of the whole menu,
        but it may be occasionally useful to delegate a single sub-menu to the
        SimpleMenu class.  Note that this parameter only affects the CSS class.
        
        active(kw): the active label, if any, in the menu.

        You must add and edit the "menu.html" file in your template directory.
        
        Example::

            <ul>
                {% for item in item_list %}
                <li{% if item.2 %} class="active"{% endif %}>
                    <a href="{{ item.1 }}">{{ item.0 }}</a>
                </li>
                {% endfor %}
            </ul>
        """
        item_list = []
        for label, view in self.menus[menu_name]:
            item_list.append((gettext(label), reverse(view), view == active))
        context = template.Context({'item_list': item_list, 'depth': depth})
        return loader.get_template('menu.html').render(context)

menu = SimpleMenu(settings.MENU_ITEMS)

class MenuNode(template.Node):
    """
    The menu tag takes a menu path whose components are labels separated by spaces.
    All the components from the first to the next-to-last are menu labels, and
    they are going to be rendered as menu bars.  Since they are seen as
    sub-items, or (if you will) as nested tabs in a web page, each component
    is also the active component in the previous menu.
    
    The last component is not rendered as a menu, but it is taken to be the
    active item in the last menu (that is, the next-to-last component).


    Usage example::
        
        {% menu root venue_menu new_visit %}

        will render the 'root' menu with the 'venue_menu' item, if it exists, as
        active; then the 'venue_menu_ menu with the 'new_visit' item, if it
        exists, as active.
    """
    def __init__(self, menu_path):
        self.menu_path = menu_path

    def render(self, context):
        # Item = (item, follower)
        for i in range(len(self.menu_path)):
            # Strip any single quotes from the string edges
            self.menu_path = [s.rstrip('"\'').lstrip('"\'')
                for s in self.menu_path]
        self.context = context
        # Render each couple: (1,2), (2,3), (3,4), ...
        return ''.join([self._render_menu(self.menu_path[index],    
            active=self.menu_path[index+1], depth=index)
            for index in range(len(self.menu_path)-1)])

    def _render_menu(self, menu_name, active=None, depth=None):
        """
        If the menu has its own template, then use the template.  Otherwise,
        ask its class to do the rendering.
        """
        try:
            menu_template = loader.get_template('menu/%s.html' % menu_name)
            self.context['active'] = active
            return menu_template.render(self.context)
        except template.TemplateDoesNotExist:
            return menu.render(menu_name, depth=depth, active=active)

def do_menu(parser, token):
    menu_path = token.split_contents()
    return MenuNode(menu_path[1:])

register.tag('menu', do_menu)

# http://www.djangosnippets.org/snippets/1153/

def do_ifactive(parser, token):
    """
    Defines a conditional block tag, "ifactive" that switches based on whether the active request 
    is being handled by a particular view (with optional args and kwargs).
    
    Has the form:
    
    {% ifactive request path.to.view %}
        [Block to render if path.to.view is the active view]
    {% else %}
        [Block to render if path.to.view is not the active view]
    {% endifactive %}

    'request' is a context variable expression which resolves to the HttpRequest object for the current
    request. (Additionally, the ActiveViewMiddleware must be installed for this to work.)

    'path.to.view' can be a string with a python import path (which must be mentioned in the urlconf),
    or a name of a urlpattern (i.e., same as the argument to the {% url %} tag).
    
    You can also pass arguments or keyword arguments in the same form as accepted by the {% url %} tag,
    e.g.:
    
    {% ifactive request path.to.view var1="bar",var2=var.prop %}...{% endifactive %}   
    
    or:
    
    {% ifactive request path.to.view "bar",var.prop %}...{% endifactive %}   
    
    The else block is optional.
    """

    end_tag = 'endifactive'

    active_nodes = parser.parse((end_tag,'else'))    
    end_token = parser.next_token()
    if end_token.contents == 'else':
        inactive_nodes = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        inactive_nodes = None

    tag_args = token.contents.split(' ')
    if len(tag_args) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (context variable with the request, and path to a view)" % tag_args[0])
    
    request_var = tag_args[1]
    view_name = tag_args[2]
    args, kwargs = _parse_url_args(parser, tag_args[3:])
    
    return ActiveNode(request_var, view_name, args, kwargs, active_nodes, inactive_nodes)
       
register.tag('ifactive', do_ifactive)

class ActiveNode(Node):
    def __init__(self, request_var, view_name, args, kwargs, active_nodes, inactive_nodes=None):
        self.request_var = request_var
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.active_nodes = active_nodes
        self.inactive_nodes = inactive_nodes
    
    def render(self, context):        

        request = resolve_variable(self.request_var, context)

        view, default_args = _get_view_and_default_args(self.view_name)        
                
        if getattr(request, '_view_func', None) is view:        
            
            resolved_args = [arg.resolve(context) for arg in self.args]                                               
            if request._view_args == resolved_args:
            
                resolved_kwargs = dict([(k, v.resolve(context)) for k, v in self.kwargs.items()])
                resolved_kwargs.update(default_args)
                                               
                if request._view_kwargs == resolved_kwargs:
                    return self.active_nodes.render(context)
        
        if self.inactive_nodes is not None:    
            return self.inactive_nodes.render(context)
        else:
            return ''

def _get_patterns_map(resolver, default_args=None):
    """
    Recursively generates a map of 
    (pattern name or path to view function) -> (view function, default args)    
    """

    patterns_map = {}
    
    if default_args is None:
        default_args = {}

    for pattern in resolver.url_patterns:
    
        pattern_args = default_args.copy()
    
        if isinstance(pattern, RegexURLResolver):
            pattern_args.update(pattern.default_kwargs)
            patterns_map.update(_get_patterns_map(pattern, pattern_args))
        else:
            pattern_args.update(pattern.default_args)
        
            if pattern.name is not None:
                patterns_map[pattern.name] = (pattern.callback, pattern_args)
            
            # HACK: Accessing private attribute of RegexURLPattern
            callback_str = getattr(pattern, '_callback_str', None)
            if callback_str is not None:    
                patterns_map[pattern._callback_str] = (pattern.callback, pattern_args)
        
    return patterns_map    

_view_name_cache = None

def _get_view_and_default_args(view_name):
    """
    Given view_name (a path to a view or a name of a urlpattern,
    returns the view function and a dict containing any default kwargs
    that are specified in the urlconf for that view.
    """

    global _view_name_cache
    
    if _view_name_cache is None:
        _view_name_cache = _get_patterns_map(get_resolver(None))               
        
    try:
        return _view_name_cache[view_name]
    except KeyError:
        raise KeyError("%s does not match any urlpatterns" % view_name)   
    
def _parse_url_args(parser, bits):
    """
    Parses URL parameters in the same way as the {% url %} tag.    
    """

    args = []
    kwargs = {}
    
    for bit in bits:
        for arg in bit.split(","):
            if '=' in arg:
                k, v = arg.split('=', 1)
                k = k.strip()
                kwargs[smart_str(k,'ascii')] = parser.compile_filter(v)
            elif arg:
                args.append(parser.compile_filter(arg))
    
    return args, kwargs
