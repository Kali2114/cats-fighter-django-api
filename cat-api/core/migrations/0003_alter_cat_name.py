# Generated by Django 5.0.4 on 2024-05-06 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cat',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
