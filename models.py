import uuid

from sqlalchemy import BOOLEAN
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import INTEGER
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import TEXT
from sqlalchemy import TIMESTAMP
from sqlalchemy import UniqueConstraint
from sqlalchemy import VARCHAR
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

engine = create_engine('postgresql:///localizappion')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))  # type: Session

Base = declarative_base()

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


class Language(Base):
    __tablename__ = 'language'

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


class Project(Base):
    __tablename__ = 'project'

    id = Column(INTEGER, primary_key=True, nullable=False)
    uuid = Column(VARCHAR(40), nullable=False, unique=True, default=generate_uuid)
    name = Column(VARCHAR(128), nullable=False, unique=True)

    strings_upload_time = Column(TIMESTAMP, nullable=True)


class String(Base):
    __tablename__ = 'string'
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


Project.strings = relationship(String, order_by=String.position, cascade='delete')


class Translation(Base):
    __tablename__ = 'translation'

    id = Column(INTEGER, primary_key=True, nullable=False)
    project_id = Column(INTEGER, ForeignKey(Project.id), nullable=False)
    language_id = Column(INTEGER, ForeignKey(Language.id), nullable=False)

    project = relationship(Project, back_populates='translations')
    language = relationship(Language)

    # def count_accepted_suggestions(self):
    #     count = 0
    #     for plural_form in self.language.plural_forms:
    #         count += String.objects.distinct().filter(
    #             project=self.project,
    #             suggestions__translation=self,
    #             suggestions__plural_form=plural_form,
    #             suggestions__accepted=True
    #         ).count()
    #     return count
    #
    # def count_required_suggestions(self):
    #     plurals = self.project.strings.exclude(value_one='').count()
    #     return plurals * len(self.language.plural_forms) + self.project.strings.count() - plurals


Project.translations = relationship(Translation, cascade='delete')


class Translator(Base):
    __tablename__ = 'translator'

    id = Column(INTEGER, primary_key=True, nullable=False)
    uuid = Column(VARCHAR(40), nullable=False, unique=True, default=generate_uuid)
    alias = Column(VARCHAR(32), nullable=True)


class Suggestion(Base):
    __tablename__ = 'suggestion'
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
    added_time = Column(TIMESTAMP, default=func.now())

    translation = relationship(Translation, back_populates='suggestions')
    translator = relationship(Translator, back_populates='suggestions')
    string = relationship(String, back_populates='suggestions')


Translation.suggestions = relationship(Suggestion, cascade='delete')
Translator.suggestions = relationship(Suggestion, cascade='delete')
String.suggestions = relationship(Suggestion, cascade='delete', lazy='dynamic')


class Vote(Base):
    __tablename__ = 'suggestion_vote'
    __table_args__ = (
        PrimaryKeyConstraint('suggestion_id', 'translator_id'),
    )

    suggestion_id = Column(INTEGER, ForeignKey(Suggestion.id), nullable=False)
    translator_id = Column(INTEGER, ForeignKey(Translator.id), nullable=False)
    value = Column(INTEGER, nullable=False, default=1)

    suggestion = relationship(Suggestion, cascade='delete', back_populates='votes')
    translator = relationship(Translator, cascade='delete')

    def __str__(self):
        return str(self.translator)


Suggestion.votes = relationship(Vote)
Suggestion.votes_value = column_property(select([func.sum(Vote.value)]).where(Vote.suggestion_id == Suggestion.id))
