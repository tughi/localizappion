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
        ordering = ('name',)


class Project(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)

    strings_upload_time = models.DateTimeField(null=True, blank=True)

    def count_new_suggestions(self):
        return Suggestion.objects.filter(translation__project=self, accepted=None).count()

    def __str__(self):
        return self.name


class Translation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='+')

    def count_accepted_suggestions(self):
        count = 0
        for plural_form in self.language.plural_forms:
            count += String.objects.distinct().filter(
                project=self.project,
                suggestions__translation=self,
                suggestions__plural_form=plural_form,
                suggestions__accepted=True
            ).count()
        return count

    def count_required_suggestions(self):
        plurals = self.project.strings.exclude(value_one='').count()
        return plurals * len(self.language.plural_forms) + self.project.strings.count() - plurals

    def __str__(self):
        return '{0}::{1}'.format(self.project.name, self.language.code)

    class Meta:
        ordering = ('language__name',)


class String(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='strings')
    name = models.CharField(max_length=64)
    value_one = models.TextField(blank=True)
    value_other = models.TextField()
    markers = models.TextField(blank=True)
    position = models.IntegerField(default=0)

    last_access_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}::{1}'.format(self.project.name, self.name)

    class Meta:
        ordering = ('position', 'name')
        unique_together = (
            ('project', 'name'),
        )


class Translator(models.Model):
    uuid = models.UUIDField(unique=True, editable=False)
    alias = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.alias or str(self.uuid)


class Suggestion(models.Model):
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE, related_name='suggestions')
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE, related_name='suggestions')
    string = models.ForeignKey(String, on_delete=models.CASCADE, related_name='suggestions')
    value = models.TextField()
    plural_form = models.CharField(max_length=8, choices=PLURAL_FORMS, default='other')
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    accepted = models.NullBooleanField()
    added_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0} =({1}::{2})= {3}'.format(self.string.name, self.translation, self.plural_form, self.value)

    class Meta:
        unique_together = (
            ('translation', 'string', 'value', 'plural_form'),
        )


class Vote(models.Model):
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE)
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField(default=1)

    def __str__(self):
        return str(self.translator)

    class Meta:
        unique_together = (
            ('translator', 'suggestion'),
        )


def __on_suggestion_post_saved__(sender, instance, created, **kwargs):
    if sender == Suggestion and created:
        Vote.objects.create(translator=instance.translator, suggestion=instance)


models.signals.post_save.connect(__on_suggestion_post_saved__, Suggestion)
