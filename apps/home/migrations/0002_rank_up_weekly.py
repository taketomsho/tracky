# Generated by Django 3.2.8 on 2022-07-17 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rank',
            name='up_weekly',
            field=models.IntegerField(null=True),
        ),
    ]
