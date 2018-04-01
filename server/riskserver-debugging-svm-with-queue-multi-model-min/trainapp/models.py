from __future__ import unicode_literals

import os
from django.db import models

from riskserver import settings


# Create your models here.

class Train(models.Model):
    imei = models.CharField(max_length=100)
    path = models.CharField(max_length=10000)

    def __unicode__(self):
        return self.imei


class User(models.Model):
    imei = models.CharField(unique=True, max_length=100)
    joined_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.imei


def uploaded_file_path(instance, filename):
    return '{0}/{1}/{2}/{3}/{4}'.format(
        instance.type, instance.user.imei, instance.state, instance.group_id,
        instance.file_name)


def uploaded_arff_file_path(instance, filename):
    return '{0}/{1}/{2}/{3}/{4}'.format(
        instance.type, instance.user.imei, instance.state, instance.group_id,
        instance.file_name + '.arff')


def uploaded_libsvm_file_path(instance, filename):
    return '{0}/{1}/{2}/{3}/{4}'.format(
        instance.type, instance.user.imei, instance.state, instance.group_id,
        instance.file_name + '.libsvm')


class UploadedFile(models.Model):
    user = models.ForeignKey(User, verbose_name='user')

    # relative path to UPLOADED_DIR
    path = models.FileField(upload_to=uploaded_file_path)
    arff_path = models.FileField(upload_to=uploaded_arff_file_path)
    libsvm_path = models.FileField(upload_to=uploaded_libsvm_file_path)
    # uploaded file name
    file_name = models.CharField(max_length=1000)

    is_lie = models.BooleanField(default=True)
    # grouped by a PARAMETER
    group_id = models.IntegerField()
    # type with choices 'train' or 'test'
    type = models.CharField(max_length=5)
    # state with choices 'sit' or 'walk'
    state = models.CharField(default='sit', max_length=4)

    is_dispatched = models.BooleanField(default=False)
    target_model_box_order = models.IntegerField(verbose_name='target model box', default=0)
    is_trained = models.BooleanField(default=False)
    target_model_order = models.IntegerField(verbose_name='target model', default=0)
    is_active = models.BooleanField(default=True)

    joined_time = models.DateTimeField(auto_now=True)

    # override
    # you can delete records and files together in admin interface
    def delete(self, using=None):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.path.path))
        super(UploadedFile, self).delete()

    def __unicode__(self):
        return '{0}_{1}_{2}'.format(self.user, self.path, self.joined_time)


class ModelBox(models.Model):
    user = models.ForeignKey(User, verbose_name='user')

    model_box_path = models.FilePathField(path=settings.MODEL_BOX_ROOT, allow_folders=True, allow_files=False,
                                          max_length=1000, recursive=True, blank=False)
    # state with choices 'sit' or 'walk'
    state = models.CharField(default='sit', max_length=4)
    model_box_order = models.IntegerField(blank=False)
    joined_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'user:{0} state:{1} order:{2}'.format(self.user, self.state, self.model_box_order)


class BoxDispatchingCheckAccuracy(models.Model):
    model_box = models.ForeignKey(ModelBox)
    file = models.ForeignKey(UploadedFile)
    # accuracy is generated when a certain group of uploaded files match with all existing latest models
    # but we regard them as 'accuracy go into or not a model box'
    accuracy = models.CharField(max_length=30)


class Model(models.Model):
    user = models.ForeignKey(User, verbose_name='user')
    model_box = models.ForeignKey(ModelBox)

    model_path = models.FilePathField(path=settings.MODEL_BOX_ROOT, allow_folders=False, allow_files=True,
                                      max_length=1000, recursive=True)

    model_order = models.IntegerField(default=0)

    model_latest = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    joined_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{0}'.format(self.model_path)

    def delete(self, using=None):
        os.remove(os.path.join(self.model_path))
        super(Model, self).delete()
