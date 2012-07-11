# -*- coding: utf-8 -*-

import StringIO
import sys
import unittest

from flask import Flask
from flask.ext.script import Command, Manager, InvalidCommand, Option


class SimpleCommand(Command):
    "simple command"

    def run(self):
        print "OK"


class CommandWithArgs(Command):
    "command with args"

    option_list = (
        Option("name"),
    )

    def run(self, name):
        print name


class CommandWithOptions(Command):
    "command with options"

    option_list = (
        Option("-n", "--name",
               help="name to pass in",
               dest="name"),
    )

    def run(self, name):
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

    def run(self, name):
        print name


class CommandWithCatchAll(Command):
    "command with catch all args"

    capture_all_args = True

    def get_options(self):
        return (Option('--foo', dest='foo',
                       action='store_true'),)

    def run(self, remaining_args, foo):
        print remaining_args


class TestCommands(unittest.TestCase):

    TESTING = True

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)


class TestManager(unittest.TestCase):

    TESTING = True

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)

    def test_with_default_commands(self):

        manager = Manager(self.app)

        assert 'runserver' in manager._commands
        assert 'shell' in manager._commands

    def test_without_default_commands(self):

        manager = Manager(self.app, with_default_commands=False)

        assert 'runserver' not in manager._commands
        assert 'shell' not in manager._commands

    def test_add_command(self):

        manager = Manager(self.app)
        manager.add_command("simple", SimpleCommand())

        assert isinstance(manager._commands['simple'], SimpleCommand)

    def test_simple_command_decorator(self):

        manager = Manager(self.app)

        @manager.command
        def hello():
            print "hello"

        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello")
        assert 'hello' in sys.stdout.getvalue()

    def test_simple_command_decorator_with_pos_arg(self):

        manager = Manager(self.app)

        @manager.command
        def hello(name):
            print "hello", name

        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello", ["joe"])
        assert 'hello joe' in sys.stdout.getvalue()

    def test_command_decorator_with_options(self):

        manager = Manager(self.app)

        @manager.command
        def hello(name='fred'):
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

        try:
            manager.handle("manage.py", "hello", ["--help"])
        except SystemExit:
            pass
        assert 'Prints your name' in sys.stdout.getvalue()

    def test_command_decorator_with_boolean_options(self):

        manager = Manager(self.app)

        @manager.command
        def verify(verified=False):
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
        def hello(name, url=None):
            if url:
                assert type(url) is unicode
                print "hello", name, "from", url
            else:
                assert type(name) is unicode
                print "hello", name

        assert 'hello' in manager._commands

        manager.handle("manage.py", "hello", ["joe"])
        assert 'hello joe' in sys.stdout.getvalue()

        manager.handle("manage.py", "hello", ["joe", '--url=reddit.com'])
        assert 'hello joe from reddit.com' in sys.stdout.getvalue()

    def test_command_decorator_with_additional_options(self):

        manager = Manager(self.app)

        @manager.option('-n', '--name', dest='name', help='Your name')
        def hello(name):
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
        def hello_again(name, url=None):
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

        assert "simple     simple command" in manager.get_usage()

    def test_get_usage_with_specified_usage(self):

        manager = Manager(self.app, usage="hello")
        manager.add_command("simple", SimpleCommand())

        usage = manager.get_usage()
        assert "simple     simple command" in usage
        assert "hello" in usage

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
            manager.run({'simple': SimpleCommand()})
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

    def test_run_catch_all(self):
        manager = Manager(self.app)
        manager.add_command("catch", CommandWithCatchAll())
        sys.argv = ["manage.py", "catch", "pos1", "--foo", "pos2", "--bar"]
        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 0
        assert "['pos1', 'pos2', '--bar']" in sys.stdout.getvalue()

    def test_run_bad_options(self):
        manager = Manager(self.app)
        manager.add_command("simple", CommandWithOptions())
        sys.argv = ["manage.py", "simple", "--foo=bar"]
        try:
            sys_stderr_orig = sys.stderr
            sys.stderr = StringIO.StringIO()
            manager.run()
        except SystemExit, e:
            assert e.code == 2
        finally:
            sys.stderr = sys_stderr_orig

    def test_init_with_flask_instance(self):
        manager = Manager(self.app)
        assert callable(manager.app)

    def test_init_with_callable(self):
        manager = Manager(lambda: app)
        assert callable(manager.app)

    def test_raise_index_error(self):

        manager = Manager(self.app)

        @manager.command
        def error():
            raise IndexError()

        try:
            self.assertRaises(IndexError, manager.run, default_command="error")
        except SystemExit, e:
            assert e.code == 1

    def test_run_with_default_command(self):
        manager = Manager(self.app)
        manager.add_command('simple', SimpleCommand())
        try:
            manager.run(default_command='simple')
        except SystemExit, e:
            assert e.code == 0
        assert 'OK' in sys.stdout.getvalue()


class TestSubManager(unittest.TestCase):

    TESTING = True

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)

    def test_add_submanager(self):

        sub_manager = Manager()

        manager = Manager(self.app)
        manager.add_command("sub_manager", sub_manager)

        assert isinstance(manager._commands['sub_manager'], Manager)
        assert sub_manager.parent == manager
        assert sub_manager.get_options() == manager.get_options()

    def test_run_submanager_command(self):

        sub_manager = Manager()
        sub_manager.add_command("simple", SimpleCommand())

        manager = Manager(self.app)
        manager.add_command("sub_manager", sub_manager)

        sys.argv = ["manage.py", "sub_manager", "simple"]

        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 0

        assert 'OK' in sys.stdout.getvalue()

    def test_manager_usage_with_submanager(self):

        sub_manager = Manager(usage="Example sub-manager")

        manager = Manager(self.app)
        manager.add_command("sub_manager", sub_manager)

        sys.argv = ["manage.py"]

        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 1

        assert 'sub_manager  Example sub-manager' in sys.stdout.getvalue()

    def test_submanager_usage(self):

        sub_manager = Manager(usage="Example sub-manager")
        sub_manager.add_command("simple", SimpleCommand())

        manager = Manager(self.app)
        manager.add_command("sub_manager", sub_manager)

        sys.argv = ["manage.py", "sub_manager"]

        try:
            manager.run()
        except SystemExit, e:
            assert e.code == 1

        assert "simple  simple command" in sys.stdout.getvalue()

    def test_submanager_no_default_commands(self):

        sub_manager = Manager()

        manager = Manager()
        manager.add_command("sub_manager", sub_manager)

        assert 'runserver' not in sub_manager._commands
        assert 'shell' not in sub_manager._commands
