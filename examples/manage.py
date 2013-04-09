#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import pprint

from flask import Flask, current_app
from flask.ext.script import Manager, prompt_choices, Server
from flask.ext.script.commands import ShowUrls, Clean


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
    print type(name)


@manager.command
def outputplus(name, url=None):
    "print name and url"
    print name, url


@manager.command
def getrolesimple():

    choices = ("member", "moderator", "admin")

    role = prompt_choices("role", choices=choices, default="member")
    print "ROLE:", role


@manager.command
def getrole():

    choices = (
        (1, "member"),
        (2, "moderator"),
        (3, "admin"),
    )

    role = prompt_choices("role", choices=choices, resolve=int, default=1)
    print "ROLE:", role


@manager.option('-n', '--name', dest='name', help="your name")
@manager.option('-u', '--url', dest='url', help="your url")
def optional(name, url):
    "print name and url"
    print name, url

manager.add_option("-c", "--config",
                   dest="config",
                   help="config file",
                   required=False)

manager.add_command("runservernoreload", Server(use_reloader=False))
manager.add_command("urls", ShowUrls())
manager.add_command("clean", Clean())

if __name__ == "__main__":
    manager.run()
