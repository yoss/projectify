# Generated by Django 4.1.3 on 2023-01-07 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0006_rename_contract_name_contract_name_and_more'),
        ('projects', '0003_project_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(related_name='members', to='employees.employee'),
        ),
    ]
