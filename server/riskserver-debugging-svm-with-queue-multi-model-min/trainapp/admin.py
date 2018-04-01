# Register your models here.

from django.contrib import admin
from django.utils.translation import ugettext_lazy

from trainapp.models import User, UploadedFile, ModelBox, Model, BoxDispatchingCheckAccuracy

# from django.contrib.admin.actions import delete_selected
admin.site.disable_action('delete_selected')


def delete_selected(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


class UserAdmin(admin.ModelAdmin):
    list_display = ['imei', 'joined_time']
    list_filter = ['joined_time']
    ordering = ['-joined_time']
    actions = ['delete_selected']
delete_selected.short_description = ugettext_lazy("Delete selected %(verbose_name_plural)s")


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['user', 'file_name', 'group_id', 'is_lie', 'state', 'type',
                    'is_dispatched','is_active',  'target_model_box_order','is_trained', 'target_model_order',
                    'joined_time']
    list_filter = ['user__imei', 'is_lie', 'state', 'type', 'is_dispatched', 'is_active', 'is_trained']
    ordering = ['-joined_time']
    actions = [delete_selected]


class ModelBoxAdmin(admin.ModelAdmin):
    list_display = ['user', 'state', 'model_box_order', 'joined_time']
    list_filter = ['user__imei', 'state', 'joined_time']
    actions = [delete_selected]


class ModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'model_box', 'model_latest', 'is_active', 'model_order', 'joined_time']
    list_filter = ['user__imei', 'model_latest', 'joined_time', 'model_box__state']
    actions = [delete_selected]


class BoxDCAAdmin(admin.ModelAdmin):
    list_display = ['model_box', 'accuracy']
    list_filter = ['model_box__user', 'model_box__state']
    actions = ['delete_selected']


admin.site.register(User, UserAdmin)
admin.site.register(UploadedFile, UploadedFileAdmin)
admin.site.register(ModelBox, ModelBoxAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(BoxDispatchingCheckAccuracy, BoxDCAAdmin)
