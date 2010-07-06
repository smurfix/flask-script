# -*- coding: utf-8 -*-

import sys
import unittest

from flask import Flask
from flaskext.script import Command, Manager, InvalidCommand, Option

class SimpleCommand(Command):
    description = "simple command"

    def run(self, app):
        print "OK"


class CommandWithArgs(Command):
    description = "command with args"

    option_list = (
        Option("name"),
    )

    def run(self, app, name):
        print name


class CommandWithOptions(Command):
    description = "command with options"

    option_list = (
        Option("-n", "--name", 
               help="name to pass in",
               dest="name"),
    )

    def run(self, app, name):
        print name


class CommandWithDynamicOptions(Command):
    description = "command with options"

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


