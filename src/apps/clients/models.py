from django.db import models
from ..base.models import unique_slugify

class Client(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def update_slug(self, string_to_slugify):
        if self.slug != string_to_slugify:
            self.slug = unique_slugify(self, string_to_slugify)
            self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super(Client, self).save(*args, **kwargs)
