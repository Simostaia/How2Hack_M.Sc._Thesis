# Generated by Django 2.1.15 on 2021-12-14 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20211214_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='ssh_psw',
            field=models.CharField(default='brcgFCO0ouc8Gz9RSisYraDrMl1vFw4b40TdmDC2Zs0mHXROd4DcY9coS886sYuYjAOCIodF7I8D1D1UQpu3cHHNvEAPbsVQ0vg3E6B3HB2CH1UHPU8yONb', max_length=120),
        ),
        migrations.AlterField(
            model_name='webssh',
            name='webssh_server',
            field=models.CharField(default='http://3.89.188.106:8888', max_length=120),
        ),
    ]
