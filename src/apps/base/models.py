from django.utils.crypto import get_random_string
from slugify import slugify

def unique_slugify(instance, string_to_slugify, restricted_slugs=[]):
    slug_value = slugify(string_to_slugify)
    model = instance.__class__
    hardcoded_restricted_slugs = ['add', 'exec', 'all', 'api']
    
    restricted_slugs = restricted_slugs + hardcoded_restricted_slugs
    if slug_value in restricted_slugs:
        slug_value = slug_value + get_random_string(length=4)
    if model.objects.filter(slug=slug_value).exists():
        slug_value = unique_slugify(instance,  slug_value + get_random_string(length=4))
    return slug_value