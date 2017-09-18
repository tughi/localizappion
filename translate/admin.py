from django.contrib import admin

from .models import Language
from .models import Project
from .models import String
from .models import Suggestion
from .models import Translator

admin.site.register(Language)
admin.site.register(Project)
admin.site.register(String)
admin.site.register(Translator)
admin.site.register(Suggestion)
