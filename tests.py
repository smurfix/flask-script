import sys
import unittest

from optparse import make_option

from flask import Flask
from flaskext.script import Command, Manager, InvalidCommand

class SimpleCommand(Command):
    help = "simple command"

    def run(self, app):
        print "OK"


class CommandWithArgs(Command):
    help = "command with args"
    args = '[NAME]'

    def run(self, app, name):
        print name


class CommandWithOptions(Command):
    help = "command with options"
    args = 'foo'

    option_list = (
        make_option("-n", "--name", 
                    help="name to pass in",
                    dest="name"),
    )

    def run(self, app, name):
        print name


class TestCommands(unittest.TestCase):

    TESTING = True

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)

    def test_usage_simple(self):

        command = SimpleCommand()

        assert 'simple command' in command.usage("simple")

    def test_usage_custom(self):

        command = CommandWithArgs()

        assert '[NAME]' in command.usage("simple")


class TestManager(unittest.TestCase):
    
    TESTING = True

    def setUp(self):
        
        self.app = Flask(__name__)
        self.app.config.from_object(self)

    def test_register(self):

        manager = Manager(self.app)
        manager.register("simple", SimpleCommand())
        
        assert isinstance(manager._commands['simple'], SimpleCommand)

    def test_run_existing_command(self):
        
        manager = Manager(self.app)
        manager.register("simple", SimpleCommand())
        manager.run_command("manage.py", "simple")
        assert 'OK' in sys.stdout.getvalue()

    def test_run_non_existant_command(self):

        manager = Manager(self.app)
        self.assertRaises(InvalidCommand, 
                           manager.run_command,
                           "manage.py", "simple")
    
    def test_run_existing(self):

        manager = Manager(self.app)
        manager.register("simple", SimpleCommand())
        sys.argv = ["manage.py", "simple"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 0
        assert 'OK' in sys.stdout.getvalue()

    def test_run_not_existing(self):

        manager = Manager(self.app)
        sys.argv = ["manage.py", "simple"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 1
        assert 'OK' not in sys.stdout.getvalue()

    def test_run_no_name(self):

        manager = Manager(self.app)
        sys.argv = ["manage.py"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 1
        assert "No command provided" in sys.stdout.getvalue()

    def test_run_bad_options(self):

        manager = Manager(self.app)
        manager.register("simple", CommandWithOptions())
        sys.argv = ["manage.py", "simple", "--foo=bar"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 2


