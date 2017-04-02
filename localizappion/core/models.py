from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Language(models.Model):
    code = models.SlugField(primary_key=True, verbose_name='Language code')
    name = models.CharField(max_length=100, verbose_name='Language name')

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User)

    def __str__(self):
        return self.name


class Text(models.Model):
    project = models.ForeignKey(Project)
    key = models.CharField(primary_key=True, max_length=256)
    value = models.TextField()


class Translation(models.Model):
    text = models.ForeignKey(Text)
    language = models.ForeignKey(Language)
    value = models.TextField()


class Suggestion(models.Model):
    language = models.ForeignKey(Language)
    text = models.ForeignKey(Text)
    value = models.TextField()
    votes = models.ManyToManyField(User)

