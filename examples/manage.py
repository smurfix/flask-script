import pprint

from flask import Flask
from flaskext.script import Manager, Command, Option, Shell, Server

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG', silent=True)
    return app

manager = Manager(create_app)

@manager.command
def dumpconfig(app):
    "Dumps config"
    pprint.pprint(app.config)

@manager.command
def output(app, name):
    "print something"
    print name

manager.add_command("shell", Shell())
manager.add_command("runserver", Server())

print manager._commands

if __name__ == "__main__":
    manager.run()
