# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-18 21:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(unique=True)),
                ('name', models.TextField()),
                ('plurals_zero', models.TextField(blank=True)),
                ('plurals_one', models.TextField(blank=True)),
                ('plurals_two', models.TextField(blank=True)),
                ('plurals_few', models.TextField(blank=True)),
                ('plurals_many', models.TextField(blank=True)),
                ('plurals_other', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.TextField()),
                ('languages', models.ManyToManyField(related_name='_project_languages_+', to='translate.Language')),
            ],
        ),
        migrations.CreateModel(
            name='String',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('value_one', models.TextField(blank=True)),
                ('value_other', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strings', to='translate.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.TextField()),
                ('plural_form', models.TextField(choices=[('zero', 'Zero'), ('one', 'One'), ('two', 'Two'), ('few', 'Few'), ('many', 'Many'), ('other', 'Other')], default='other')),
                ('google_translation', models.TextField(blank=True)),
                ('accepted', models.BooleanField()),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='translate.Language')),
                ('string', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to='translate.String')),
            ],
        ),
        migrations.CreateModel(
            name='SuggestionVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=1)),
                ('suggestion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='translate.Suggestion')),
            ],
        ),
        migrations.CreateModel(
            name='Translator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(editable=False, unique=True)),
                ('alias', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='suggestionvote',
            name='translator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='translate.Translator'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='translator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='translate.Translator'),
        ),
        migrations.AlterUniqueTogether(
            name='suggestionvote',
            unique_together=set([('translator', 'suggestion')]),
        ),
        migrations.AlterUniqueTogether(
            name='suggestion',
            unique_together=set([('string', 'language', 'value', 'plural_form')]),
        ),
        migrations.AlterUniqueTogether(
            name='string',
            unique_together=set([('project', 'name')]),
        ),
    ]
