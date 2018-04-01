# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='train',
            name='imei',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='imei',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
