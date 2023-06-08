# Generated by Django 4.2.1 on 2023-06-04 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0011_remove_userprofile_following_userprofile_saved_list"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="following",
            field=models.ManyToManyField(
                blank=True, related_name="followers", to="app.userprofile"
            ),
        ),
    ]
