import pprint

from flask import Flask
from flaskext.script import Manager, Command, Option, Shell, Server

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG', silent=True)
    return app

manager = Manager(create_app)

class DumpConfig(Command):

    help = "Dumps config"

    def run(self, app):
        pprint.pprint(app.config)

class PrintSomething(Command):

    help = "print something"

    option_list = (
        Option("-n", "--name", dest="name"),
    )

    def run(self, app, name=''):
        print name

manager.add_command("dumpconfig", DumpConfig())
manager.add_command("print", PrintSomething())
manager.add_command("shell", Shell())
manager.add_command("runserver", Server())

if __name__ == "__main__":
    manager.run()
