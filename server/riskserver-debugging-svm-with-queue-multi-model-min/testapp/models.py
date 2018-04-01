from __future__ import unicode_literals

from django.db import models


# Create your models here.
from trainapp.models import User, Model


class TestRecord(models.Model):
    test_user = models.ForeignKey(User, related_name='test_user')
    target_user = models.ForeignKey(User, related_name='target_user')
    # state with choices 'sit' or 'walk'
    state = models.CharField(default='sit', max_length=4)
    group_id = models.IntegerField()
    is_valid = models.BooleanField(default=True)
    # model existing is not equivalent to model box existing
    # when there is no model in any box, we just set model_exists=False
    # and the parameters below are to be 0
    model_exists = models.BooleanField()
    # this group will be tested by 'model_tested'
    model_box_order = models.IntegerField(default=0)
    model_order = models.IntegerField(default=0)
    accuracy = models.CharField(max_length=30, default='0.0')
    precision = models.CharField(max_length=30, default='0.0')
    recall = models.CharField(max_length=30, default='0.0')

