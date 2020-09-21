from django.contrib import admin
from .models import Activity, Actor, Verb, SlackField


class SlackFieldAdmin(admin.ModelAdmin):
    model = SlackField
    list_display = ('verb', 'slack_event_field',
                    'expected_value')
    list_filter = ('verb__display_name', 'slack_event_field', 'expected_value')
    fieldsets = [
        (None, { 'fields': [
            ('slack_event_field',), ('expected_value',), ('verb',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class ActorAdmin(admin.ModelAdmin):
    model = Actor
    list_display = ('iri', 'iri_type', 'display_name', 'slack_user_id')
    list_filter = ('iri', 'iri_type', 'display_name', 'slack_user_id')
    fieldsets = [
        (None, { 'fields': [
            ('iri',), ('iri_type',), ('display_name',), ('slack_user_id',),
            ('object_type',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class VerbAdmin(admin.ModelAdmin):
    model = Verb
    list_display = ('iri', 'display_name', 'language')
    list_filter = ('iri', 'display_name', 'language')
    fieldsets = [
        (None, { 'fields': [
            ('iri',), ('display_name',), ('language',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


class ActivityAdmin(admin.ModelAdmin):
    model = Activity
    list_display = ('iri', 'display_name', 'language')
    list_filter = ('iri', 'display_name', 'language')
    fieldsets = [
        (None, { 'fields': [
            ('iri',), ('display_name',), ('language',), ('description',),
            ('activity_type',), ('more_info',), ('object_type',)]
            }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            print("Obj: ", obj.__dict__)
            obj.created_by_id = request.user.id
        obj.save()


admin.site.register(Activity, ActivityAdmin)
admin.site.register(Actor, ActorAdmin)
admin.site.register(Verb, VerbAdmin)
admin.site.register(SlackField, SlackFieldAdmin)
