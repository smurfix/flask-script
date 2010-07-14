# -*- coding: utf-8 -*-

import sys
import unittest

from flask import Flask
from flaskext.script import Command, Manager, InvalidCommand, Option

class SimpleCommand(Command):
    "simple command"

    def run(self, app):
        print "OK"


class CommandWithArgs(Command):
    "command with args"

    option_list = (
        Option("name"),
    )

    def run(self, app, name):
        print name


class CommandWithOptions(Command):
    "command with options"

    option_list = (
        Option("-n", "--name", 
               help="name to pass in",
               dest="name"),
    )

    def run(self, app, name):
        print name


class CommandWithDynamicOptions(Command):
    "command with options"

    def __init__(self, default_name='Joe'):
        self.default_name = default_name

    def get_options(self):

        return ( 
            Option("-n", "--name", 
                   help="name to pass in",
                   dest="name",
                   default=self.default_name),
            )

    def run(self, app, name):
        print name


class TestCommands(unittest.TestCase):

    TESTING = True

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)

    def test_create_with_args_parser(self):

        command = CommandWithArgs()

        parser = command.create_parser("manage.py", "simple")

        ns = parser.parse_args(["Joe"])
        assert ns.name == "Joe"

    def test_create_with_options_parser(self):

        command = CommandWithOptions()

        parser = command.create_parser("manage.py", "simple")

        ns = parser.parse_args(["--name=Joe"])
        assert ns.name == "Joe"
    
    def test_create_with_dynamic_options_parser(self):

        command = CommandWithDynamicOptions("Fred")

        parser = command.create_parser("manage.py", "simple")

        ns = parser.parse_args([])
        assert ns.name == "Fred"

class TestManager(unittest.TestCase):
    
    TESTING = True

    def setUp(self):
        
        self.app = Flask(__name__)
        self.app.config.from_object(self)

    def test_add_command(self):

        manager = Manager(self.app)
        manager.add_command("simple", SimpleCommand())
        
        assert isinstance(manager._commands['simple'], SimpleCommand)

    def test_simple_command_decorator(self):

        manager = Manager(self.app)
        
        @manager.command
        def hello(app):
            print "hello"

        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello")
        assert 'hello' in sys.stdout.getvalue()

    def test_simple_command_decorator_with_pos_arg(self):

        manager = Manager(self.app)
        
        @manager.command
        def hello(app, name):
            print "hello", name
        

        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello", ["joe"])
        assert 'hello joe' in sys.stdout.getvalue()

    def test_command_decorator_with_options(self):

        manager = Manager(self.app)
        
        @manager.command
        def hello(app, name='fred'):
            "Prints your name"
            print "hello", name

        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello", ["--name=joe"])
        assert 'hello joe' in sys.stdout.getvalue()

        manager.handle("manage.py", "hello", ["-n joe"])
        assert 'hello joe' in sys.stdout.getvalue()

        try:
            manager.handle("manage.py", "hello", ["-h"])
        except SystemExit:
            pass
        assert 'Prints your name' in sys.stdout.getvalue()

    def test_command_decorator_with_boolean_options(self):

        manager = Manager(self.app)
        
        @manager.command
        def verify(app, verified=False):
            "Checks if verified"
            print "VERIFIED ?", "YES" if verified else "NO"

        assert 'verify' in manager._commands

        manager.handle("manage.py", "verify", ["--verified"])
        assert 'YES' in sys.stdout.getvalue()

        manager.handle("manage.py", "verify", ["-v"])
        assert 'YES' in sys.stdout.getvalue()

        manager.handle("manage.py", "verify", [])
        assert 'NO' in sys.stdout.getvalue()

        try:
            manager.handle("manage.py", "verify", ["-h"])
        except SystemExit:
            pass
        assert 'Checks if verified' in sys.stdout.getvalue()

    def test_simple_command_decorator_with_pos_arg_and_options(self):

        manager = Manager(self.app)
        
        @manager.command
        def hello(app, name, url=None):
            if url:
                print "hello", name, "from", url
            else:
                print "hello", name
        
        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello", ["joe"])
        assert 'hello joe' in sys.stdout.getvalue()

        manager.handle("manage.py", "hello", ["joe", '--url=reddit.com'])
        assert 'hello joe from reddit.com' in sys.stdout.getvalue()

    def test_command_decorator_with_additional_options(self):

        manager = Manager(self.app)
        
        @manager.option('-n', '--name', dest='name', help='Your name')
        def hello(app, name):
            print "hello", name

        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello", ["--name=joe"])
        assert 'hello joe' in sys.stdout.getvalue()

        try:
            manager.handle("manage.py", "hello", ["-h"])
        except SystemExit:
            pass
        assert "Your name" in sys.stdout.getvalue()

        @manager.option('-n', '--name', dest='name', help='Your name')
        @manager.option('-u', '--url', dest='url', help='Your URL')
        def hello_again(app, name, url=None):
            if url:
                print "hello", name, "from", url
            else:
                print "hello", name

        assert 'hello_again' in manager._commands

        manager.handle("manage.py", "hello_again", ["--name=joe"])
        assert 'hello joe' in sys.stdout.getvalue()

        manager.handle("manage.py", "hello_again", 
            ["--name=joe", "--url=reddit.com"])
        assert 'hello joe from reddit.com' in sys.stdout.getvalue()

    def test_get_usage(self):

        manager = Manager(self.app)
        manager.add_command("simple", SimpleCommand())

        assert manager.get_usage() == "simple: simple command"

    def test_run_existing_command(self):
        
        manager = Manager(self.app)
        manager.add_command("simple", SimpleCommand())
        manager.handle("manage.py", "simple")
        assert 'OK' in sys.stdout.getvalue()

    def test_run_non_existant_command(self):

        manager = Manager(self.app)
        self.assertRaises(InvalidCommand, 
                           manager.handle,
                           "manage.py", "simple")
    
    def test_run_existing(self):

        manager = Manager(self.app)
        manager.add_command("simple", SimpleCommand())
        sys.argv = ["manage.py", "simple"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 0
        assert 'OK' in sys.stdout.getvalue()

    def test_run_existing_bind_later(self):

        manager = Manager(self.app)
        sys.argv = ["manage.py", "simple"]
        try:
            manager.run({'simple':SimpleCommand()})
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
            assert e.code == 0

    def test_run_good_options(self):

        manager = Manager(self.app)
        manager.add_command("simple", CommandWithOptions())
        sys.argv = ["manage.py", "simple", "--name=Joe"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 0
        assert "Joe" in sys.stdout.getvalue()

    def test_run_dynamic_options(self):

        manager = Manager(self.app)
        manager.add_command("simple", CommandWithDynamicOptions('Fred'))
        sys.argv = ["manage.py", "simple"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 0
        assert "Fred" in sys.stdout.getvalue()

    def test_run_bad_options(self):

        manager = Manager(self.app)
        manager.add_command("simple", CommandWithOptions())
        sys.argv = ["manage.py", "simple", "--foo=bar"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 2

    def test_init_with_flask_instance(self):
        
        manager = Manager(self.app)
        assert callable(manager.app_factory)

    def test_init_with_callable(self):

        manager = Manager(lambda: app)
        assert callable(manager.app_factory)

