# Generated by Django 2.0.5 on 2018-06-06 21:30

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('added_time', models.DateTimeField(auto_now_add=True)),
                ('activation_code', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('activated_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='String',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('value_one', models.TextField(blank=True)),
                ('value_other', models.TextField()),
                ('markers', models.TextField(blank=True)),
                ('position', models.IntegerField(default=0)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strings', to='l11n.Project')),
            ],
            options={
                'ordering': ('position', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_zero', models.TextField(blank=True)),
                ('value_one', models.TextField(blank=True)),
                ('value_two', models.TextField(blank=True)),
                ('value_few', models.TextField(blank=True)),
                ('value_many', models.TextField(blank=True)),
                ('value_other', models.TextField(blank=True)),
                ('accepted', models.NullBooleanField()),
                ('added_time', models.DateTimeField(auto_now_add=True)),
                ('string', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to='l11n.String')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('language', models.CharField(choices=[('ar', 'Arabic'), ('be', 'Belarusian'), ('bg', 'Bulgarian'), ('ca', 'Catalan'), ('zh-Hans', 'Chinese (Simplified Han)'), ('zh-Hant', 'Chinese (Traditional Han)'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('nl', 'Dutch'), ('et', 'Estonian'), ('fi', 'Finnish'), ('fr', 'French'), ('de', 'German'), ('el', 'Greek'), ('iw', 'Hebrew'), ('hi', 'Hindi'), ('hu', 'Hungarian'), ('in', 'Indonesian'), ('it', 'Italian'), ('ja', 'Japanese'), ('ko', 'Korean'), ('lv', 'Latvian'), ('lt', 'Lithuanian'), ('nb', 'Norwegian Bokmål'), ('nn', 'Norwegian Nynorsk'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('es', 'Spanish'), ('sv', 'Swedish'), ('th', 'Thai'), ('tr', 'Turkish'), ('uk', 'Ukrainian'), ('vi', 'Vietnamese')], max_length=8)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='l11n.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Translator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_hash', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggestion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='votes', to='l11n.Suggestion')),
                ('translator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='votes', to='l11n.Translator')),
            ],
        ),
        migrations.AddField(
            model_name='suggestion',
            name='translation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to='l11n.Translation'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='translator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='suggestions', to='l11n.Translator'),
        ),
        migrations.AddField(
            model_name='session',
            name='translator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sessions', to='l11n.Translator'),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together={('suggestion', 'translator')},
        ),
        migrations.AlterUniqueTogether(
            name='suggestion',
            unique_together={('translation', 'string', 'value_zero', 'value_one', 'value_two', 'value_few', 'value_many', 'value_other')},
        ),
        migrations.AlterUniqueTogether(
            name='string',
            unique_together={('project', 'name')},
        ),
    ]
