# Generated by Django 3.2.8 on 2022-06-30 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rank',
            name='url',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='rank',
            name='date',
            field=models.DateField(null=True),
        ),
    ]
