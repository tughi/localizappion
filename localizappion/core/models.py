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

    def strings_count(self):
        return self.strings.count()


class String(models.Model):
    project = models.ForeignKey(Project, related_name='strings')
    key = models.CharField(max_length=256)
    value = models.TextField()

    def __str__(self):
        return self.key


class Translation(models.Model):
    string = models.ForeignKey(String)
    language = models.ForeignKey(Language)
    value = models.TextField()

    def key(self):
        return self.string.key

    def default(self):
        return self.string.value

    def language_code(self):
        return self.language.code

    def project(self):
        return self.string.project


class Suggestion(models.Model):
    translator = models.ForeignKey(User, related_name='suggestions')
    language = models.ForeignKey(Language)
    string = models.ForeignKey(String)
    value = models.TextField()
    votes = models.ManyToManyField(User, blank=True, related_name='voted_suggestion')

    def key(self):
        return self.string.key

    def default(self):
        return self.string.value

    def language_code(self):
        return self.language.code

    def project(self):
        return self.string.project

    def votes_count(self):
        return self.votes.count()
