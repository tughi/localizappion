from uuid import uuid4 as generate_uuid

from django.db import models

from .languages import LANGUAGES


class Project(models.Model):
    uuid = models.UUIDField(unique=True, default=generate_uuid, editable=False)
    name = models.CharField(unique=True, max_length=64)


class String(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='strings')
    name = models.CharField(max_length=64)
    value_one = models.TextField(blank=True)
    value_other = models.TextField()
    markers = models.TextField(blank=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ('position', 'name')
        unique_together = (
            ('project', 'name'),
        )


class Translator(models.Model):
    email_hash = models.TextField(unique=True)


class Session(models.Model):
    uuid = models.UUIDField(unique=True, default=generate_uuid, editable=False)
    translator = models.ForeignKey(Translator, on_delete=models.PROTECT, related_name='sessions')
    added_time = models.DateTimeField(auto_now_add=True)
    activation_code = models.UUIDField(unique=True, default=generate_uuid, editable=False)
    activated_time = models.DateTimeField(null=True)


class Translation(models.Model):
    uuid = models.UUIDField(unique=True, default=generate_uuid, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=8, choices=sorted([(l['code'], l['name']) for l in LANGUAGES], key=lambda l: l[1]))


class Suggestion(models.Model):
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE, related_name='suggestions')
    translator = models.ForeignKey(Translator, on_delete=models.PROTECT, related_name='suggestions')
    string = models.ForeignKey(String, on_delete=models.CASCADE, related_name='suggestions')
    value_zero = models.TextField(blank=True)
    value_one = models.TextField(blank=True)
    value_two = models.TextField(blank=True)
    value_few = models.TextField(blank=True)
    value_many = models.TextField(blank=True)
    value_other = models.TextField(blank=True)
    accepted = models.NullBooleanField()
    added_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('translation', 'string', 'value_zero', 'value_one', 'value_two', 'value_few', 'value_many', 'value_other'),
        )


class Vote(models.Model):
    suggestion = models.ForeignKey(Suggestion, on_delete=models.PROTECT, related_name='votes')
    translator = models.ForeignKey(Translator, on_delete=models.PROTECT, related_name='votes')

    class Meta:
        unique_together = (
            ('suggestion', 'translator'),
        )
