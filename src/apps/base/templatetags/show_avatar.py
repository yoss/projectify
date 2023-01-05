from django import template

register = template.Library()

@register.inclusion_tag('templatetags/show_avatar.html')
def show_avatar(employee):
    return({'employee': employee})