from django.contrib import admin
from .models import Employee, Contract, Rate

# Register your models here.
admin.site.register(Employee)
admin.site.register(Contract)
admin.site.register(Rate)

