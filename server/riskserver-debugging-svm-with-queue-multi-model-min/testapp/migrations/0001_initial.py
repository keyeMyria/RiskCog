# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(default='sit', max_length=4)),
                ('group_id', models.IntegerField()),
                ('is_valid', models.BooleanField(default=True)),
                ('model_exists', models.BooleanField()),
                ('model_box_order', models.IntegerField(default=0)),
                ('model_order', models.IntegerField(default=0)),
                ('accuracy', models.CharField(default='0.0', max_length=30)),
                ('precision', models.CharField(default='0.0', max_length=30)),
                ('recall', models.CharField(default='0.0', max_length=30)),
                ('target_user', models.ForeignKey(related_name='target_user', to='trainapp.User')),
                ('test_user', models.ForeignKey(related_name='test_user', to='trainapp.User')),
            ],
        ),
    ]
