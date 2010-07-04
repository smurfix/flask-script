import pprint

from flask import Flask, current_app
from flaskext.script import Manager

from optparse import make_option

def create_app():
    return Flask(__name__)

manager = Manager(create_app)

@manager.register('dumpconf')
def dump_config():
    pprint.pprint(current_app.config)

@manager.register('printme', 
                  options=(make_option('-n', '--name'),))
def printme(name):
    print name

if __name__ == "__main__":
    manager.run()
