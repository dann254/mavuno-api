# Generated by Django 3.1.6 on 2021-02-19 18:45
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0001_initial')
    ]

    operations = [
        CreateExtension('postgis')
    ]
