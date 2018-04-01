# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainapp', '0001_initial'),
        ('visualization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label_begin', models.IntegerField(default=100)),
                ('model_number', models.IntegerField(default=0)),
                ('description', models.CharField(max_length=30)),
                ('user', models.ForeignKey(to='trainapp.User')),
            ],
        ),
    ]
