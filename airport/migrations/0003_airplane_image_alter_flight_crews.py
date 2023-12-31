# Generated by Django 4.2.6 on 2023-10-23 00:54

import airport.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0002_alter_airplane_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="airplane",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airport.models.airplane_image_path
            ),
        ),
        migrations.AlterField(
            model_name="flight",
            name="crews",
            field=models.ManyToManyField(
                blank=True, related_name="flights", to="airport.crew"
            ),
        ),
    ]
