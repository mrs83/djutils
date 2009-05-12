from django import template
from django.contrib.comments.models import Comment

register = template.Library()

class UserCommentCountNode(template.Node):
    def __init__(self, user, context_var):
        self.user = user
        self.context_var = context_var

    def render(self, context):
        user = template.Variable(self.user).resolve(context)
        count = Comment.objects.filter(user=user, is_public=True).count()
        context[self.context_var] = count
        return ''

def do_get_comment_count_for_user(parser, token):
    """
    Get user's comment count as context template variable

    Usage::
        
        {% get_comment_count_for_user user as comment_count %}
    """
    bits = token.contents.split()
    if len(bits) < 4:
        raise template.TemplateSyntaxError, "tag takes 3 arguments"
    if bits[2] != 'as':
        raise template.TemplateSyntaxError, "2rd argument must be 'as'"
    return UserCommentCountNode(bits[1], bits[3])

register.tag('get_comment_count_for_user', do_get_comment_count_for_user)
