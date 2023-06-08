# Generated by Django 4.2.1 on 2023-06-02 12:14

import app.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "img",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=app.models.user_directory_path_posts,
                        verbose_name="Image",
                    ),
                ),
                ("caption", models.CharField(max_length=4094, verbose_name="Caption")),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                (
                    "poster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name_plural": "Posts",},
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bio", models.TextField(blank=True, null=True)),
                (
                    "pfp",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=app.models.user_directory_path_profile,
                        verbose_name="Profile Picture",
                    ),
                ),
                ("location", models.CharField(blank=True, max_length=64, null=True)),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("favorites", models.ManyToManyField(blank=True, to="app.post")),
                (
                    "following",
                    models.ManyToManyField(
                        blank=True, related_name="followers", to="app.userprofile"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CommentPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField(verbose_name="")),
                ("comment_date", models.DateTimeField(auto_now_add=True)),
                (
                    "commentor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="commentor",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="app.post",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Comments",},
        ),
    ]
