# Register your models here.
from django.contrib import admin

from query.models import Score


class ScoreAdmin(admin.ModelAdmin):
    list_display = ['test_user', 'target_user', 'version', 'accuracy']
    list_filter = ['test_user__imei', 'target_user__imei']
    actions = ['delete_selected']


admin.site.register(Score, ScoreAdmin)
