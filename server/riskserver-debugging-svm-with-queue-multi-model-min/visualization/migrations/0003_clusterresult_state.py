# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualization', '0002_clusterresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusterresult',
            name='state',
            field=models.CharField(default='sit', max_length=5),
            preserve_default=False,
        ),
    ]
