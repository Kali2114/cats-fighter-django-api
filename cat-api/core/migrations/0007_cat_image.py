# Generated by Django 5.0.4 on 2024-05-15 16:22

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_fightingstyles_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='cat',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.cat_image_file_path),
        ),
    ]
