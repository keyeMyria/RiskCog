from __future__ import unicode_literals
from django.db import models

# Create your models here.
from trainapp.models import User


class Score(models.Model):
    test_user = models.ForeignKey(User, related_name='test_user_score')
    target_user = models.ForeignKey(User, related_name='target_user_score')
    version = models.IntegerField(default=0)
    accuracy = models.CharField(max_length=30)
