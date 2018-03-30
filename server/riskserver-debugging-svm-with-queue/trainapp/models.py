from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Train(models.Model):
    imei = models.CharField(max_length=30)
    path = models.CharField(max_length=10000)

    def __unicode__(self):
        return self.username
