# Generated by Django 2.1.15 on 2021-12-06 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20211202_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='macchinaattacco',
            name='username',
            field=models.CharField(default='root', max_length=120),
        ),
        migrations.AlterField(
            model_name='user',
            name='ssh_psw',
            field=models.CharField(default='aDpPs0bRt6GVCesV6NfEXeqa3fZjTFezqXrD6rQCkTN75Q8IdxI69Mvp0ZURJOhcobFz9oGuinqbV7tlLiKWMyjAe3QWG4XgslVrgGgr9ONDWWlWf3SR5Dd', max_length=120),
        ),
    ]
