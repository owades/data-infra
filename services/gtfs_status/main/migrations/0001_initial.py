# Generated by Django 4.0.2 on 2022-02-16 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bucket",
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
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="BucketHour",
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
                ("date", models.DateField()),
                ("hour", models.IntegerField()),
                (
                    "times",
                    models.JSONField(
                        default=list,
                        help_text="A sorted list list of times that files were requested.",
                    ),
                ),
                (
                    "bucket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.bucket"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Feed",
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
                ("itp_id", models.IntegerField()),
                ("url_type", models.CharField(max_length=64)),
                ("url_index", models.IntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "active"), ("disabled", "disabled")],
                        default="active",
                        max_length=16,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FeedHour",
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
                    "files_at_times",
                    models.JSONField(
                        default=list,
                        help_text="A list of 1s and 0s indicating if a file exists.",
                    ),
                ),
                (
                    "buckethour",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.buckethour",
                    ),
                ),
                (
                    "feed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.feed"
                    ),
                ),
            ],
        ),
    ]
