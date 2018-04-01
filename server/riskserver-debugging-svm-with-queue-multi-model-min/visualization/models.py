from django.db import models

# Create your models here.
from riskserver import data_source
from trainapp.models import User


class TestResult(models.Model):
    test_user = models.ForeignKey(User, related_name='test_user_visualization')
    target_user = models.ForeignKey(User, related_name='target_user_visualization')
    self_verification = models.BooleanField(default=True)
    acceptance_accuracy = models.CharField(max_length=30)
    valid = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    ratio = models.CharField(max_length=30)


class ClusterResult(models.Model):
    user = models.ForeignKey(User)
    label_begin = models.IntegerField(default=data_source.LABEL_BEGIN)
    state = models.CharField(max_length=5)
    model_number = models.IntegerField(default=0)
    description = models.CharField(max_length=30)
