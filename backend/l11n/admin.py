from django.contrib import admin

from .models import Project
from .models import Session
from .models import String
from .models import Suggestion
from .models import Translation
from .models import Translator
from .models import Vote

admin.site.register(Project)
admin.site.register(Session)
admin.site.register(String)
admin.site.register(Suggestion)
admin.site.register(Translation)
admin.site.register(Translator)
admin.site.register(Vote)
