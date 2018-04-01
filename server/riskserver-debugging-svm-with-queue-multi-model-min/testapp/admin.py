# Register your models here.

from django.contrib import admin

from testapp.models import TestRecord


class TestRecordAdmin(admin.ModelAdmin):
    list_display = ['test_user', 'target_user', 'state', 'group_id', 'is_valid', 'model_exists', 'model_box_order',
                    'accuracy', 'precision', 'recall']
    list_filter = ['test_user__imei', 'target_user__imei', 'state', 'is_valid', 'model_box_order']
    actions = ['delete_selected']


admin.site.register(TestRecord, TestRecordAdmin)
