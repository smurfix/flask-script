import pprint

from flask import Flask, current_app
from flaskext.script import Manager

def create_app(config=None):
    app = Flask(__name__)
    app.debug = False
    print "CONFIG", config

    app.config.from_envvar('APP_CONFIG', silent=True)

    @app.route("/")
    def index():
        # deliberate error, test debug working
        assert False, "oops"

    return app

manager = Manager(create_app)

@manager.command
def dumpconfig():
    "Dumps config"
    pprint.pprint(current_app.config)

@manager.command
def output(name):
    "print something"
    print name

@manager.command
def outputplus(name, url=None):
    "print name and url"
    print name, url

@manager.option('-n', '--name', dest='name', help="your name")
@manager.option('-u', '--url', dest='url', help="your url")
def optional(name, url):
    "print name and url"
    print name, url

manager.add_option("-c", "--config", 
                   dest="config", 
                   help="config file", 
                   required=False)

if __name__ == "__main__":
    manager.run()
