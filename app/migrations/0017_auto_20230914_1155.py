# Generated by Django 2.1.15 on 2023-09-14 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20230913_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ctfd_configs',
            name='token_API',
            field=models.CharField(max_length=69),
        ),
        migrations.AlterField(
            model_name='user',
            name='ssh_psw',
            field=models.CharField(default='BK4AAQtAswxJhqJkGNlJh5XEEgjs5TfNR1pvXRwp7Ke9yKjusZxAOAS3Vr1lkZeWCU4f9RKYOL2aeNWdE9s8TXN1IzEwrMuUnt1serN59mxlU85EXPqLZwx', max_length=120),
        ),
    ]
