# Generated by Django 2.1.15 on 2023-09-14 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20230914_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='ssh_psw',
            field=models.CharField(default='qoZxOuR89RPFkv7DtD8ZSg28gicwX9bIpOmly4g2vAOCyhzaCZQMJXeIPl43dEYK0ogVFewLMSSDyxHAL0dlicAuD4qqv09RIfoc4jLsCTSNNkoYTWngRRk', max_length=120),
        ),
    ]
