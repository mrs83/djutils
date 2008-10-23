"""
Based on http://www.djangosnippets.org/snippets/347/
"""

from django import template
from django.template import loader
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()

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
            item_list.append((label, reverse(view), view == active))
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
