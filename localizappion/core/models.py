import uuid

from django.db import models

PLURAL_FORMS = (
    ('zero', "Zero"),
    ('one', "One"),
    ('two', "Two"),
    ('few', "Few"),
    ('many', "Many"),
    ('other', "Other")
)


class Language(models.Model):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=64)

    plurals_zero = models.CharField(max_length=128, blank=True)
    plurals_one = models.CharField(max_length=128, blank=True)
    plurals_two = models.CharField(max_length=128, blank=True)
    plurals_few = models.CharField(max_length=128, blank=True)
    plurals_many = models.CharField(max_length=128, blank=True)
    plurals_other = models.CharField(max_length=128, blank=True)

    @property
    def plural_forms(self):
        plural_forms = []
        if self.plurals_zero:
            plural_forms.append('zero')
        if self.plurals_one:
            plural_forms.append('one')
        if self.plurals_two:
            plural_forms.append('two')
        if self.plurals_few:
            plural_forms.append('few')
        if self.plurals_many:
            plural_forms.append('many')
        if self.plurals_other:
            plural_forms.append('other')
        return tuple(plural_forms)

    def get_examples(self, plural_form):
        if plural_form == 'zero':
            return self.plurals_zero
        if plural_form == 'one':
            return self.plurals_one
        if plural_form == 'two':
            return self.plurals_two
        if plural_form == 'few':
            return self.plurals_few
        if plural_form == 'many':
            return self.plurals_many
        if plural_form == 'other':
            return self.plurals_other
        return None

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'localizappion_language'


class Project(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)

    languages = models.ManyToManyField(Language, related_name='+')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'localizappion_project'


class String(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='strings')
    name = models.CharField(max_length=64)
    value_one = models.TextField(blank=True)
    value_other = models.TextField()
    position = models.IntegerField(default=0)

    last_access_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'localizappion_string'
        ordering = ('position',)
        unique_together = (
            ('project', 'name'),
        )


class Translator(models.Model):
    uuid = models.UUIDField(unique=True, editable=False)
    alias = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.alias or str(self.uuid)

    class Meta:
        db_table = 'localizappion_translator'


class Suggestion(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    translator = models.ForeignKey(Translator, on_delete=models.PROTECT)
    string = models.ForeignKey(String, on_delete=models.CASCADE, related_name='suggestions')
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    value = models.TextField()
    plural_form = models.CharField(max_length=8, choices=PLURAL_FORMS, default='other')

    google_translation = models.TextField(blank=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return '{0} =({1}::{2})= {3}'.format(self.string.name, self.language.code, self.plural_form, self.value)

    class Meta:
        db_table = 'localizappion_suggestion'
        unique_together = (
            ('string', 'language', 'value', 'plural_form'),
        )


class Vote(models.Model):
    translator = models.ForeignKey(Translator, on_delete=models.PROTECT)
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField(default=1)

    def __str__(self):
        return str(self.translator)

    class Meta:
        db_table = 'localizappion_vote'
        unique_together = (
            ('translator', 'suggestion'),
        )


def __on_suggestion_post_saved__(sender, instance, created, **kwargs):
    if sender == Suggestion and created:
        Vote.objects.create(translator=instance.translator, suggestion=instance)


models.signals.post_save.connect(__on_suggestion_post_saved__, Suggestion)