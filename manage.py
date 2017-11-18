#!/usr/bin/env python
from flask_script import Manager
from flask_script import Server
from flask_script import Shell

from localizappion import app

manager = Manager(app)
manager.add_command("runserver", Server())
manager.add_command("shell", Shell())
manager.run()
