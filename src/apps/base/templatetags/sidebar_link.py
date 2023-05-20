from django.urls import reverse
from django import template


register = template.Library()

@register.inclusion_tag('templatetags/sidebar_link.html', takes_context=True)
def sidebar_link(context, title, permission, link, icon = 'arrow-right-circle'):
    active = ''
    allowed = False
    # if context['request'].resolver_match.app_name == link.split(":")[0]: active = 'active'
    if context['request'].resolver_match.app_name == link.split(":")[0]: active = 'active'
    if context['request'].user.has_perm(permission): allowed = True
    return({'title': title, 'allowed': allowed, 'link': link, 'icon': icon, 'active': active})
