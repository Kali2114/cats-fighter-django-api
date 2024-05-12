# Generated by Django 5.0.4 on 2024-05-12 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_ability_cat_abilities'),
    ]

    operations = [
        migrations.CreateModel(
            name='FightingStyles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('BX', 'Boks'), ('KB', 'Kickboxing'), ('MT', 'Muay Thai'), ('WR', 'Wrestling'), ('BJJ', 'Brazilian Jiu-Jitsu')], max_length=50)),
                ('ground_allowed', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='cat',
            name='fighting_styles',
            field=models.ManyToManyField(to='core.fightingstyles'),
        ),
    ]
