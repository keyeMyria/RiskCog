from django.contrib import admin

from visualization.models import TestResult, ClusterResult


class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_user', 'target_user',
                    'self_verification', 'acceptance_accuracy',
                    'valid', 'total', 'ratio']
    list_filter = ['test_user__imei', 'target_user__imei']
    actions = ['delete_selected']


class ClusterResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'label_begin', 'state', 'model_number', 'description']
    list_filter = ['user', 'label_begin']
    actions = ['delete_selected']

admin.site.register(TestResult, TestResultAdmin)
admin.site.register(ClusterResult, ClusterResultAdmin)
