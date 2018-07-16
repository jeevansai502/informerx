# Generated by Django 2.0 on 2018-07-15 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informer', '0003_email_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Groups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=256)),
                ('groupname', models.CharField(max_length=256)),
            ],
        ),
        migrations.RemoveField(
            model_name='user_details',
            name='groupname',
        ),
    ]
