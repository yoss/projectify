from django.db import models
from django.urls import reverse
from ..base.models import unique_slugify

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    is_chargable = models.BooleanField(default=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, blank=True, null=True)
    managers = models.ManyToManyField('employees.Employee', related_name='managers')
    members = models.ManyToManyField('employees.Employee', related_name='members')

    def __str__(self):
        return self.name

    def update_slug(self, string_to_slugify):
        if self.slug != string_to_slugify:
            self.slug = unique_slugify(self, string_to_slugify)
            self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super(Project, self).save(*args, **kwargs)

    def get_absolute_url(self): return reverse("projects:project-detail", kwargs={"slug": self.slug})
    def get_update_url(self): return reverse("projects:project-update", kwargs={"slug": self.slug})
    def get_activate_url(self): return reverse("projects:project-activate", kwargs={"slug": self.slug})
    def get_deactivate_url(self): return reverse("projects:project-deactivate", kwargs={"slug": self.slug})
    def get_update_url(self): return reverse("projects:project-update", kwargs={"slug": self.slug})
    def get_list_url(): return reverse("projects:project-list")