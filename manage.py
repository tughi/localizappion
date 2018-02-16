#!/usr/bin/env python
from flask_script import Manager
from flask_script import Server
from flask_script import Shell
from flask_migrate import MigrateCommand

from localizappion import app

manager = Manager(app)

manager.add_command("runserver", Server())
manager.add_command("shell", Shell())
manager.add_command("db", MigrateCommand)


@manager.command
def make_hash():
    from getpass import getpass
    from localizappion.utils import create_hash

    print('Secret hash: {0}'.format(create_hash(getpass('Secret: '))))


@manager.command
def db_schema():
    from localizappion.models import db
    from sqlalchemy import create_engine

    def dump(sql, *args, **kwargs):
        print(sql.compile(dialect=engine.dialect))

    engine = create_engine(db.engine.url, strategy='mock', executor=dump)
    db.metadata.create_all(engine)


manager.run()
