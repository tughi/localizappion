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


class Project(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.TextField()

    languages = models.ManyToManyField(Language, related_name='+')


class String(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='strings')
    name = models.TextField()
    value_one = models.TextField(blank=True)
    value_other = models.TextField()

    class Meta:
        unique_together = (
            ('project', 'name'),
        )


class Translator(models.Model):
    uuid = models.UUIDField(unique=True, editable=False)
    alias = models.TextField()


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
    string = models.ForeignKey(String, on_delete=models.CASCADE)
    value = models.TextField()
    plural_form = models.TextField(choices=PLURAL_FORMS, default='other')

    class Meta:
        unique_together = (
            ('string', 'value', 'plural_form'),
        )
