from django import template

register = template.Library()

@register.tag(name='captureas')
def do_captureas(parser, token):
    """
    From http://www.djangosnippets.org/snippets/545/
    
    Tags like url and trans provide no way to get the result as a context variable. But how would you get a computed URL into a blocktrans?\
    This snippet solves the general problem. Just put the template code whose output you want to capture within captureas tags. For example:

    {% captureas login_url %}{% url login %}{% endcaptureas %}
    {% blocktrans %}
    <a href="{{ login_url }}">login</a>
    {% endblocktrans %}
    """
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)

class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''
