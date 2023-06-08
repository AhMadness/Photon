# Generated by Django 4.2.1 on 2023-06-05 15:45

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0014_alter_userprofile_pfp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="pfp",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=app.models.user_directory_path_profile,
                verbose_name="Profile Picture",
            ),
        ),
    ]