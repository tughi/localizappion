import uuid

from django.db import models


class Language(models.Model):
    code = models.SlugField(unique=True)
    name = models.TextField()

    plurals_zero = models.TextField(blank=True)
    plurals_one = models.TextField(blank=True)
    plurals_two = models.TextField(blank=True)
    plurals_few = models.TextField(blank=True)
    plurals_many = models.TextField(blank=True)
    plurals_other = models.TextField()

    def __str__(self):
        return self.code


class Project(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.TextField()

    languages = models.ManyToManyField(Language, related_name='+')

    def __str__(self):
        return self.name


class String(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='strings')
    name = models.TextField()
    value_one = models.TextField(blank=True)
    value_other = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (
            ('project', 'name'),
        )


class Translator(models.Model):
    uuid = models.UUIDField(unique=True, editable=False)
    alias = models.TextField(blank=True)

    def __str__(self):
        return self.alias or str(self.uuid)


PLURAL_FORMS = (
    ('zero', "Zero"),
    ('one', "One"),
    ('two', "Two"),
    ('few', "Few"),
    ('many', "Many"),
    ('other', "Other")
)


class Suggestion(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    translator = models.ForeignKey(Translator, on_delete=models.PROTECT)
    string = models.ForeignKey(String, on_delete=models.CASCADE, related_name='suggestions')
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    value = models.TextField()
    plural_form = models.TextField(choices=PLURAL_FORMS, default='other')

    google_translation = models.TextField(blank=True)
    accepted = models.BooleanField()

    def __str__(self):
        return self.string.name

    class Meta:
        unique_together = (
            ('string', 'language', 'value', 'plural_form'),
        )


class SuggestionVote(models.Model):
    translator = models.ForeignKey(Translator, on_delete=models.PROTECT)
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField(default=1)

    def __str__(self):
        return str(self.translator)

    class Meta:
        unique_together = (
            ('translator', 'suggestion'),
        )
