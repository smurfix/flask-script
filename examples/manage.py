import pprint

from flask import Flask
from flaskext.script import Manager, Command, Shell, Server

from optparse import make_option

def create_app(config=None):
    if config:
        print "CONFIG", config
    return Flask(__name__)

manager_options = (
    make_option('-c', '--config',
                dest='config',
                type='string'),
)

manager = Manager(create_app, option_list=manager_options)

class DumpConfig(Command):

    help = "Dumps config"

    def run(self, app):
        pprint.pprint(app.config)

class PrintSomething(Command):

    help = "print something"

    option_list = (
        make_option("-n", "--name", dest="name"),
    )

    def run(self, app, name=''):
        print name

manager.register("dumpconfig", DumpConfig())
manager.register("print", PrintSomething())
manager.register("shell", Shell())
manager.register("runserver", Server())

if __name__ == "__main__":
    manager.run()
