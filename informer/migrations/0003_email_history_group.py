# Generated by Django 2.0 on 2018-06-15 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informer', '0002_auto_20180614_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='email_history',
            name='group',
            field=models.CharField(default='A', max_length=256),
            preserve_default=False,
        ),
    ]
