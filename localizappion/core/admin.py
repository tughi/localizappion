from django.contrib import admin

from .models import Language
from .models import Project
from .models import String
from .models import Suggestion
from .models import Translator
from .models import Vote


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid')


@admin.register(String)
class StringAdmin(admin.ModelAdmin):
    list_display = ('name', 'value_other', 'value_one', 'project')


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    pass


@admin.register(Translator)
class TranslatorAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'alias')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('translator', 'suggestion', 'value')