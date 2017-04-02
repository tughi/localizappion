from django.contrib import admin

from . import models


@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'strings_count', 'owner')


@admin.register(models.String)
class StringAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'project')


@admin.register(models.Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'language_code', 'value', 'default', 'project')


@admin.register(models.Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('key', 'language_code', 'value', 'default', 'project', 'votes_count', 'translator')
