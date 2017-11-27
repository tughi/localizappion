import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BOOLEAN
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import INTEGER
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import TEXT
from sqlalchemy import TIMESTAMP
from sqlalchemy import UniqueConstraint
from sqlalchemy import VARCHAR
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship

from localizappion import app

db = SQLAlchemy(app)

PLURAL_FORMS = (
    ('zero', "Zero"),
    ('one', "One"),
    ('two', "Two"),
    ('few', "Few"),
    ('many', "Many"),
    ('other', "Other")
)


def generate_uuid():
    return str(uuid.uuid4())


class Language(db.Model):
    id = Column(INTEGER, primary_key=True, nullable=False)
    code = Column(VARCHAR(8), nullable=False, unique=True)
    name = Column(VARCHAR(64))

    plurals_zero = Column(VARCHAR(128), nullable=True)
    plurals_one = Column(VARCHAR(128), nullable=True)
    plurals_two = Column(VARCHAR(128), nullable=True)
    plurals_few = Column(VARCHAR(128), nullable=True)
    plurals_many = Column(VARCHAR(128), nullable=True)
    plurals_other = Column(VARCHAR(128), nullable=True)

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


class Project(db.Model):
    id = Column(INTEGER, primary_key=True, nullable=False)
    uuid = Column(VARCHAR(40), nullable=False, unique=True, default=generate_uuid)
    name = Column(VARCHAR(128), nullable=False, unique=True)

    strings_upload_time = Column(TIMESTAMP, nullable=True)


class String(db.Model):
    __table_args__ = (
        UniqueConstraint('project_id', 'name'),
    )

    id = Column(INTEGER, primary_key=True, nullable=False)
    project_id = Column(INTEGER, ForeignKey(Project.id), nullable=False)
    name = Column(VARCHAR(64), nullable=False)
    value_one = Column(TEXT, nullable=True)
    value_other = Column(TEXT, nullable=False)
    markers = Column(TEXT, nullable=True)
    position = Column(INTEGER, default=0)

    project = relationship(Project)


Project.strings = relationship(String)
Project.strings_query = relationship(String, lazy='dynamic')


class Translation(db.Model):
    id = Column(INTEGER, primary_key=True, nullable=False)
    uuid = Column(VARCHAR(40), nullable=False, unique=True, default=generate_uuid)
    project_id = Column(INTEGER, ForeignKey(Project.id), nullable=False)
    language_id = Column(INTEGER, ForeignKey(Language.id), nullable=False)

    project = relationship(Project, back_populates='translations')
    language = relationship(Language)


Project.translations = relationship(Translation)


class Translator(db.Model):
    id = Column(INTEGER, primary_key=True, nullable=False)
    email_hash = Column(TEXT, nullable=False, unique=True)
    alias = Column(VARCHAR(32), nullable=True)


class TranslatorSession(db.Model):
    id = Column(INTEGER, primary_key=True, nullable=False)
    uuid = Column(VARCHAR(40), nullable=False, unique=True, default=generate_uuid)
    translator_id = Column(INTEGER, ForeignKey(Translator.id), nullable=False)
    added_time = Column(TIMESTAMP, nullable=False, default=func.now())
    activation_code = Column(VARCHAR(40), nullable=False, unique=True, default=generate_uuid)
    activated_time = Column(TIMESTAMP, nullable=True)

    translator = relationship(Translator)


class Suggestion(db.Model):
    __table_args__ = (
        UniqueConstraint('translation_id', 'string_id', 'value', 'plural_form'),
    )

    id = Column(INTEGER, primary_key=True, nullable=False)
    translation_id = Column(INTEGER, ForeignKey(Translation.id), nullable=False)
    translator_id = Column(INTEGER, ForeignKey(Translator.id), nullable=False)
    string_id = Column(INTEGER, ForeignKey(String.id), nullable=False)
    value = Column(TEXT, nullable=False)
    plural_form = Column(VARCHAR(8), default='other')  # choices=PLURAL_FORMS
    uuid = Column(VARCHAR(40), nullable=False, unique=True, default=generate_uuid)
    google_translation = Column(TEXT, nullable=True)
    accepted = Column(BOOLEAN, nullable=True)
    added_time = Column(TIMESTAMP, nullable=False, default=func.now())

    string = relationship(String, back_populates='suggestions')
    translation = relationship(Translation, back_populates='suggestions')
    translator = relationship(Translator, back_populates='suggestions')


String.suggestions = relationship(Suggestion)
String.suggestions_query = relationship(Suggestion, lazy='dynamic')
Translation.suggestions = relationship(Suggestion)
Translator.suggestions = relationship(Suggestion)


class SuggestionVote(db.Model):
    __table_args__ = (
        PrimaryKeyConstraint('suggestion_id', 'translator_id'),
    )

    suggestion_id = Column(INTEGER, ForeignKey(Suggestion.id), nullable=False)
    translator_id = Column(INTEGER, ForeignKey(Translator.id), nullable=False)
    value = Column(INTEGER, nullable=False, default=1)

    suggestion = relationship(Suggestion, back_populates='votes')
    translator = relationship(Translator)

    def __str__(self):
        return str(self.translator)


Suggestion.votes = relationship(SuggestionVote)
Suggestion.votes_query = relationship(SuggestionVote, lazy='dynamic')
Suggestion.votes_value = column_property(select([func.sum(SuggestionVote.value)]).where(SuggestionVote.suggestion_id == Suggestion.id))
