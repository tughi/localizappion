from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import INTEGER
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import TEXT
from sqlalchemy import TIMESTAMP
from sqlalchemy import UniqueConstraint
from sqlalchemy import VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Language(Base):
    __tablename__ = 'language'

    id = Column(INTEGER, primary_key=True, nullable=False)
    code = Column(VARCHAR(8), unique=True, nullable=False)
    name = Column(VARCHAR(256))


class Project(Base):
    __tablename__ = 'project'

    id = Column(INTEGER, primary_key=True, nullable=False)
    uuid = Column(VARCHAR(40), nullable=False, unique=True)
    name = Column(VARCHAR(128), nullable=False, unique=True)
    language_id = Column(INTEGER, ForeignKey(Language.id), nullable=False)

    language = relationship(Language)


class String(Base):
    __tablename__ = 'string'
    __table_args__ = (
        UniqueConstraint('project_id', 'name'),
    )

    id = Column(INTEGER, primary_key=True, nullable=False)
    project_id = Column(INTEGER, ForeignKey(Project.id), nullable=False)
    name = Column(VARCHAR(128), nullable=False)
    value = Column(TEXT, nullable=False)
    position = Column(INTEGER)

    project = relationship(Project, back_populates='strings')


Project.strings = relationship(String, order_by=String.position, back_populates='project', cascade='delete')


class Translator(Base):
    __tablename__ = 'translator'

    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(VARCHAR(32), unique=True, nullable=False)
    alias = Column(VARCHAR(32))


class Suggestion(Base):
    __tablename__ = 'suggestion'
    __table_args__ = (
        UniqueConstraint('string_id', 'language_id', 'value'),
    )

    id = Column(INTEGER, primary_key=True, nullable=False)
    string_id = Column(INTEGER, ForeignKey(String.id), nullable=False)
    translator_id = Column(INTEGER, ForeignKey(Translator.id), nullable=False)
    language_id = Column(INTEGER, ForeignKey(Language.id), nullable=False)
    value = Column(TEXT, nullable=False)
    google_translation = Column(TEXT, nullable=False)
    insert_time = Column(TIMESTAMP, nullable=False)

    string = relationship(String)
    language = relationship(Language)
    translator = relationship(Translator)

    def __init__(self, *args, **kwargs):
        super(Suggestion, self).__init__(*args, **kwargs)

        self.votes.append(Vote(suggestion=self, translator=self.translator, value=1))

    def __json__(self):
        return dict(
            id=self.id,
            string_id=self.string_id,
            translator_id=self.translator_id,
            language_id=self.language_id,
            value=self.value,
            google_translation=self.google_translation,
        )


String.suggestions = relationship(Suggestion, cascade='delete')


class Vote(Base):
    __tablename__ = 'vote'
    __table_args__ = (
        PrimaryKeyConstraint('suggestion_id', 'translator_id'),
    )

    suggestion_id = Column(INTEGER, ForeignKey(Suggestion.id), nullable=False)
    translator_id = Column(INTEGER, ForeignKey(Translator.id), nullable=False)
    value = Column(INTEGER, nullable=False)

    suggestion = relationship(Suggestion)
    translator = relationship(Translator)


Suggestion.votes = relationship(Vote, cascade='delete')
