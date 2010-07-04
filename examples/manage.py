import pprint

from flask import Flask, current_app
from flaskext.script import Manager

def create_app():
    return Flask(__name__)

manager = Manager(create_app)

@manager.register('dumpconf')
def dump_config():
    pprint.pprint(current_app.config)


if __name__ == "__main__":
    manager.run()
