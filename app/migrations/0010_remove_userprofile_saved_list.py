# Generated by Django 4.2.1 on 2023-06-04 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_userprofile_saved_list"),
    ]

    operations = [
        migrations.RemoveField(model_name="userprofile", name="saved_list",),
    ]