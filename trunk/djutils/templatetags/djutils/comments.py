from django import template
from django.db.models import get_model
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

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

class UserCommentsNode(template.Node):
    def __init__(self, user, context_var, model=None):
        self.user = user
        self.context_var = context_var
        self.model = model

    def render(self, context):
        user = template.Variable(self.user).resolve(context)
        queryset = Comment.objects.filter(user=user, is_public=True)
        if self.model:
            model = get_model(*self.model.split('.'))
            ctype = ContentType.objects.get_for_model(model)
            queryset = queryset.filter(content_type=ctype)
        context[self.context_var] = queryset
        return ''

def do_get_comments_for_user(parser, token):
    """
    Get user's comment count as context template variable

    Usage::
        
        {% get_comments_for_user user as comment_list %}
        {% get_comments_for_user user "blog.Post" as comment_list %}
    """
    bits = token.contents.split()
    bits_len = len(bits)
    if bits_len < 4:
        raise template.TemplateSyntaxError, "tag takes 3 arguments"
    user = bits[1]
    if bits_len == 5:
        model = bits[2]
        context_var = bits[4]
        if bits[3] != 'as':
            raise template.TemplateSyntaxError, "3rd argument must be 'as'"
    else:
        model = None
        context_var = bits[3]
        if bits[2] != 'as':
            raise template.TemplateSyntaxError, "2nd argument must be 'as'"
    return UserCommentsNode(user, context_var, model)

register.tag('get_comments_for_user', do_get_comments_for_user)
