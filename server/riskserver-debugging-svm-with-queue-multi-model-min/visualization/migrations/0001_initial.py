# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('self_verification', models.BooleanField(default=True)),
                ('acceptance_accuracy', models.CharField(max_length=30)),
                ('valid', models.IntegerField(default=0)),
                ('total', models.IntegerField(default=0)),
                ('ratio', models.CharField(max_length=30)),
                ('target_user', models.ForeignKey(related_name='target_user_visualization', to='trainapp.User')),
                ('test_user', models.ForeignKey(related_name='test_user_visualization', to='trainapp.User')),
            ],
        ),
    ]
