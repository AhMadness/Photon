# Generated by Django 4.2.1 on 2023-06-04 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_remove_post_saved_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="saved_list",
            field=models.JSONField(blank=True, null=True),
        ),
    ]