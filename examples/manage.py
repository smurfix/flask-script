import pprint

from flask import Flask, Response
from flaskext.script import Manager, Command, Option, Shell, Server

def create_app():
    app = Flask(__name__)
    app.debug = False
    app.config.from_envvar('APP_CONFIG', silent=True)

    @app.route("/")
    def index():
        # deliberate error, test debug working
        assert False, "oops"

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

@manager.command
def outputplus(app, name, url=None):
    "print name and url"
    print name, url

@manager.option('-n', '--name', dest='name', help="your name")
@manager.option('-u', '--url', dest='url', help="your url")
def optional(app, name, url):
    "print name and url"
    print name, url

manager.add_command("shell", Shell())
manager.add_command("runserver", Server(use_debugger=False))

if __name__ == "__main__":
    manager.run()
