import sys
import unittest

from optparse import make_option

from flask import Flask
from flaskext.script import Command, Manager, CommandNotFound

class SimpleCommand(Command):
    help = "simple command"

    def run(self, app):
        print "OK"


class CommandWithArgs(Command):
    help = "command with args"

    def usage(self, prog):
        return "%s NAME"

    def run(self, app, name):
        print name


class CommandWithOptions(Command):
    help = "command with options"

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

        assert command.usage("manage.py") == "manage.py simple command"

    def test_usage_custom(self):

        command = CommandWithArgs()

        assert command.usage("manage.py") == "manage.py NAME"

    def test_usage_options(self):

        command = CommandWithOptions()

        assert command.usage("manage.py") == "manage.py --name=name to pass in"


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
        self.assertRaises(CommandNotFound, 
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

    def test_run_bad_args(self):

        manager = Manager(self.app)
        sys.argv = ["manage.py"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 1
        assert "No command provided" in sys.stdout.getvalue()
