from django.contrib import admin
from .models import (XApiObject, XApiActor, XApiVerb, SlackVerbField,
                     SlackObjectField, LrsConfig, SlackField)


class SlackVerbFieldAdmin(admin.ModelAdmin):
    model = SlackVerbField
    list_display = ('xapi_verb', 'slack_event_field',
                    'expected_value', 'field_group')
    list_filter = ('xapi_verb__display_name', 'slack_event_field',
                   'expected_value', 'field_group')
    fieldsets = [
        (None, {'fields': [
            ('slack_event_field',), ('expected_value',), ('xapi_verb',),
            ('field_group',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class SlackObjectFieldAdmin(admin.ModelAdmin):
    model = SlackObjectField
    list_display = ('xapi_object', 'slack_event_field',
                    'expected_value', 'field_group')
    list_filter = ('xapi_object__display_name', 'slack_event_field',
                   'expected_value', 'field_group')
    fieldsets = [
        (None, {'fields': [
            ('slack_event_field',), ('expected_value',), ('xapi_object',),
            ('field_group',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class XApiActorAdmin(admin.ModelAdmin):
    model = XApiActor
    list_display = ('iri', 'iri_type', 'display_name', 'slack_user_id')
    list_filter = ('iri', 'iri_type', 'display_name', 'slack_user_id')
    fieldsets = [
        (None, {'fields': [
            ('iri',), ('iri_type',), ('display_name',), ('slack_user_id',),
            ('object_type',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class XApiVerbAdmin(admin.ModelAdmin):
    model = XApiVerb
    list_display = ('iri', 'display_name', 'language')
    list_filter = ('iri', 'display_name', 'language')
    fieldsets = [
        (None, {'fields': [
            ('iri',), ('display_name',), ('language',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class XApiObjectAdmin(admin.ModelAdmin):
    model = XApiObject
    list_display = ('iri', 'display_name', 'language')
    list_filter = ('iri', 'display_name', 'language')
    fieldsets = [
        (None, {'fields': [
            ('iri',), ('display_name',), ('language',), ('description',),
            ('activity_type',), ('more_info',), ('object_type',),
            ('extensions',), ('id_field',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class LrsConfigAdmin(admin.ModelAdmin):
    model = LrsConfig
    list_display = ('display_name', 'lrs_endpoint',)
    list_filter = ('display_name', 'lrs_endpoint',)


admin.site.register(XApiObject, XApiObjectAdmin)
admin.site.register(XApiActor, XApiActorAdmin)
admin.site.register(XApiVerb, XApiVerbAdmin)
admin.site.register(SlackVerbField, SlackVerbFieldAdmin)
admin.site.register(SlackObjectField, SlackObjectFieldAdmin)
admin.site.register(LrsConfig, LrsConfigAdmin)
admin.site.register(SlackField)