# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import trainapp.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BoxDispatchingCheckAccuracy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accuracy', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_path', models.FilePathField(path=b'/home/cyrus/Public/riskserver-debugging-svm-with-queue-multi-model-min/model', max_length=1000, recursive=True)),
                ('model_order', models.IntegerField(default=0)),
                ('model_latest', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('joined_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ModelBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_box_path', models.FilePathField(path=b'/home/cyrus/Public/riskserver-debugging-svm-with-queue-multi-model-min/model', max_length=1000, allow_files=False, recursive=True, allow_folders=True)),
                ('state', models.CharField(default='sit', max_length=4)),
                ('model_box_order', models.IntegerField()),
                ('joined_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Train',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('imei', models.CharField(max_length=30)),
                ('path', models.CharField(max_length=10000)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.FileField(upload_to=trainapp.models.uploaded_file_path)),
                ('arff_path', models.FileField(upload_to=trainapp.models.uploaded_arff_file_path)),
                ('libsvm_path', models.FileField(upload_to=trainapp.models.uploaded_libsvm_file_path)),
                ('file_name', models.CharField(max_length=1000)),
                ('is_lie', models.BooleanField(default=True)),
                ('group_id', models.IntegerField()),
                ('type', models.CharField(max_length=5)),
                ('state', models.CharField(default='sit', max_length=4)),
                ('is_dispatched', models.BooleanField(default=False)),
                ('target_model_box_order', models.IntegerField(default=0, verbose_name='target model box')),
                ('is_trained', models.BooleanField(default=False)),
                ('target_model_order', models.IntegerField(default=0, verbose_name='target model')),
                ('is_active', models.BooleanField(default=True)),
                ('joined_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('imei', models.CharField(unique=True, max_length=30)),
                ('joined_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='user',
            field=models.ForeignKey(verbose_name='user', to='trainapp.User'),
        ),
        migrations.AddField(
            model_name='modelbox',
            name='user',
            field=models.ForeignKey(verbose_name='user', to='trainapp.User'),
        ),
        migrations.AddField(
            model_name='model',
            name='model_box',
            field=models.ForeignKey(to='trainapp.ModelBox'),
        ),
        migrations.AddField(
            model_name='model',
            name='user',
            field=models.ForeignKey(verbose_name='user', to='trainapp.User'),
        ),
        migrations.AddField(
            model_name='boxdispatchingcheckaccuracy',
            name='file',
            field=models.ForeignKey(to='trainapp.UploadedFile'),
        ),
        migrations.AddField(
            model_name='boxdispatchingcheckaccuracy',
            name='model_box',
            field=models.ForeignKey(to='trainapp.ModelBox'),
        ),
    ]
