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
    uuid = models.UUIDField(unique=True)
    name = models.TextField()

    languages = models.ManyToManyField(Language, related_name='+')


class String(models.Model):
    """
        Contains the English text of a <string> or <plural> element.
        The convention here is that if value_one is also provided, we have to do then with a plural string.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='strings')
    name = models.TextField()
    value_one = models.TextField(blank=True)
    value_other = models.TextField()

    class Meta:
        unique_together = (('project', 'name'),)
