# -*- coding: utf-8 -*-

import sys
import unittest
import StringIO

from flask import Flask
from flask.ext.script import Command, Manager, InvalidCommand, Option


def run(command_line, manager_run, capture_stderr=False):
    '''
        Returns tuple of standard output and exit code
    '''
    sys_stderr_orig = sys.stderr

    if capture_stderr:
        sys.stderr = StringIO.StringIO()

    sys.argv = command_line.split()
    exit_code = None
    try:
        manager_run()
    except SystemExit as e:
        exit_code = e.code
    finally:
        out = sys.stdout.getvalue()
        # clear the standard output buffer
        sys.stdout.truncate(0)
        assert len(sys.stdout.getvalue()) == 0
        if capture_stderr:
            out += sys.stderr.getvalue()
        sys.stderr = sys_stderr_orig

    return out, exit_code


class SimpleCommand(Command):
    'simple command'

    def run(self):
        print 'OK'


class CommandWithArgs(Command):
    'command with args'

    option_list = (
        Option('name'),
    )

    def run(self, name):
        print name


class CommandWithOptions(Command):
    'command with options'

    option_list = (
        Option('-n', '--name',
               help='name to pass in',
               dest='name'),
    )

    def run(self, name):
        print name


class CommandWithDynamicOptions(Command):
    'command with options'

    def __init__(self, default_name='Joe'):
        self.default_name = default_name

    def get_options(self):

        return (
            Option('-n', '--name',
                   help='name to pass in',
                   dest='name',
                   default=self.default_name),
        )

    def run(self, name):
        print name


class CommandWithCatchAll(Command):
    'command with catch all args'

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
        manager.add_command('simple', SimpleCommand())

        assert isinstance(manager._commands['simple'], SimpleCommand)

    def test_simple_command_decorator(self):

        manager = Manager(self.app)

        @manager.command
        def hello():
            print 'hello'

        assert 'hello' in manager._commands

        stdout, code = run('manage.py hello', lambda: manager.run())
        assert 'hello' in stdout

    def test_simple_command_decorator_with_pos_arg(self):

        manager = Manager(self.app)

        @manager.command
        def hello(name):
            print 'hello', name

        assert 'hello' in manager._commands

        stdout, code = run('manage.py hello joe', lambda: manager.run())
        assert 'hello joe' in stdout

    def test_command_decorator_with_options(self):

        manager = Manager(self.app)

        @manager.command
        def hello(name='fred'):
            'Prints your name'
            print 'hello', name

        assert 'hello' in manager._commands

        stdout, code = run('manage.py hello --name=joe', lambda: manager.run())
        assert 'hello joe' in stdout

        stdout, code = run('manage.py hello -n joe', lambda: manager.run())
        assert 'hello joe' in stdout

        stdout, code = run('manage.py hello -h', lambda: manager.run())
        assert 'Prints your name' in stdout

        stdout, code = run('manage.py hello --help', lambda: manager.run())
        assert 'Prints your name' in stdout

    def test_command_decorator_with_boolean_options(self):

        manager = Manager(self.app)

        @manager.command
        def verify(verified=False):
            'Checks if verified'
            print 'VERIFIED ?', 'YES' if verified else 'NO'

        assert 'verify' in manager._commands

        stdout, code = run('manage.py verify --verified', lambda: manager.run())
        assert 'YES' in stdout

        stdout, code = run('manage.py verify -v', lambda: manager.run())
        assert 'YES' in stdout

        stdout, code = run('manage.py verify', lambda: manager.run())
        assert 'NO' in stdout

        stdout, code = run('manage.py verify -h', lambda: manager.run())
        assert 'Checks if verified' in stdout

    def test_simple_command_decorator_with_pos_arg_and_options(self):

        manager = Manager(self.app)

        @manager.command
        def hello(name, url=None):
            if url:
                assert type(url) is unicode
                print 'hello', name, 'from', url
            else:
                assert type(name) is unicode
                print 'hello', name

        assert 'hello' in manager._commands

        stdout, code = run('manage.py hello joe', lambda: manager.run())
        assert 'hello joe' in stdout

        stdout, code = run('manage.py hello joe --url=reddit.com', lambda: manager.run())
        assert 'hello joe from reddit.com' in stdout

    def test_command_decorator_with_additional_options(self):

        manager = Manager(self.app)

        @manager.option('-n', '--name', dest='name', help='Your name')
        def hello(name):
            print 'hello', name

        assert 'hello' in manager._commands

        stdout, code = run('manage.py hello --name=joe', lambda: manager.run())
        assert 'hello joe' in stdout

        stdout, code = run('manage.py hello -h', lambda: manager.run())
        assert 'Your name' in stdout

        @manager.option('-n', '--name', dest='name', help='Your name')
        @manager.option('-u', '--url', dest='url', help='Your URL')
        def hello_again(name, url=None):
            if url:
                print 'hello', name, 'from', url
            else:
                print 'hello', name

        assert 'hello_again' in manager._commands

        stdout, code = run('manage.py hello_again --name=joe', lambda: manager.run())
        assert 'hello joe' in stdout

        stdout, code = run('manage.py hello_again --name=joe --url=reddit.com', lambda: manager.run())
        assert 'hello joe from reddit.com' in stdout

    def test_global_option_provided_before_and_after_command(self):

        manager = Manager(self.app)
        manager.add_option('-c', '--config', dest='config_name', required=False, default='Development')
        manager.add_command('simple', SimpleCommand())

        assert isinstance(manager._commands['simple'], SimpleCommand)

        stdout, code = run('manage.py -c Development simple', lambda: manager.run())
        assert code == 0
        assert 'OK' in stdout

        stdout, code = run('manage.py simple -c Development', lambda: manager.run())
        assert code == 0
        assert 'OK' in stdout

    def test_global_option_value(self):

        def create_app(config_name='Empty'):
            print config_name
            return self.app

        manager = Manager(create_app)
        manager.add_option('-c', '--config', dest='config_name', required=False, default='Development')
        manager.add_command('simple', SimpleCommand())

        assert isinstance(manager._commands['simple'], SimpleCommand)

        stdout, code = run('manage.py simple', lambda: manager.run())
        assert code == 0
        assert 'Empty' not in stdout  # config_name is overwritten by default option value
        assert 'Development' in stdout
        assert 'OK' in stdout

        stdout, code = run('manage.py -c Before simple', lambda: manager.run())
        assert code == 0
        assert 'Before' in stdout
        assert 'OK' in stdout

        stdout, code = run('manage.py simple -c After', lambda: manager.run())
        assert code == 0
        assert 'After' in stdout
        assert 'OK' in stdout

        stdout, code = run('manage.py -c DoNotShow simple -c NewValue', lambda: manager.run())
        assert code == 0
        assert 'DoNotShow' not in stdout  # first parameter is ignored
        assert 'NewValue' in stdout       # second on is printed
        assert 'OK' in stdout

    def test_get_usage(self):

        manager = Manager(self.app)
        manager.add_command('simple', SimpleCommand())

        usage = manager.create_parser('manage.py').format_help()
        assert 'simple command' in usage

    def test_get_usage_with_specified_usage(self):

        manager = Manager(self.app, usage='hello')
        manager.add_command('simple', SimpleCommand())

        usage = manager.create_parser('manage.py').format_help()
        assert 'simple command' in usage
        assert 'hello' in usage

    def test_run_existing_command(self):

        manager = Manager(self.app)
        manager.add_command('simple', SimpleCommand())
        stdout, code = run('manage.py simple', lambda: manager.run())
        assert 'OK' in stdout

    def test_run_non_existant_command(self):

        manager = Manager(self.app)
        self.assertRaises(SystemExit, manager.handle, 'manage.py', 'simple')

    def test_run_existing(self):

        manager = Manager(self.app)
        manager.add_command('simple', SimpleCommand())

        stdout, code = run('manage.py simple', lambda: manager.run())
        assert 0 == code
        assert 'OK' in stdout

    def test_run_existing_bind_later(self):

        manager = Manager(self.app)

        stdout, code = run('manage.py simple', lambda: manager.run({'simple': SimpleCommand()}))
        assert code == 0
        assert 'OK' in stdout

    def test_run_not_existing(self):

        manager = Manager(self.app)

        stdout, code = run('manage.py simple', lambda: manager.run())
        assert code == 2
        assert 'OK' not in stdout

    def test_run_no_name(self):

        manager = Manager(self.app)

        stdout, code = run('manage.py', lambda: manager.run())
        assert code == 2

    def test_run_good_options(self):

        manager = Manager(self.app)
        manager.add_command('simple', CommandWithOptions())

        stdout, code = run('manage.py simple --name=Joe', lambda: manager.run())
        assert code == 0
        assert 'Joe' in stdout

    def test_run_dynamic_options(self):

        manager = Manager(self.app)
        manager.add_command('simple', CommandWithDynamicOptions('Fred'))

        stdout, code = run('manage.py simple', lambda: manager.run())
        assert code == 0
        assert 'Fred' in stdout

    def test_run_catch_all(self):
        manager = Manager(self.app)
        manager.add_command('catch', CommandWithCatchAll())

        stdout, code = run('manage.py catch pos1 --foo pos2 --bar', lambda: manager.run())
        assert code == 0
        assert "['pos1', 'pos2', '--bar']" in stdout

    def test_run_bad_options(self):
        manager = Manager(self.app)
        manager.add_command('simple', CommandWithOptions())

        stdout, code = run('manage.py simple --foo=bar', lambda: manager.run(), capture_stderr=True)
        assert code == 2

    def test_init_with_flask_instance(self):
        manager = Manager(self.app)
        assert callable(manager.app)

    def test_init_with_callable(self):
        manager = Manager(lambda: self.app)
        assert callable(manager.app)

    def test_raise_index_error(self):

        manager = Manager(self.app)

        @manager.command
        def error():
            raise IndexError()

        try:
            self.assertRaises(IndexError, run, 'manage.py error', lambda: manager.run())
        except SystemExit, e:
            assert e.code == 1

    def test_run_with_default_command(self):
        manager = Manager(self.app)
        manager.add_command('simple', SimpleCommand())

        stdout, code = run('manage.py', lambda: manager.run(default_command='simple'))
        assert code == 0
        assert 'OK' in stdout


class TestSubManager(unittest.TestCase):

    TESTING = True

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)

    def test_add_submanager(self):

        sub_manager = Manager()

        manager = Manager(self.app)
        manager.add_command('sub_manager', sub_manager)

        assert isinstance(manager._commands['sub_manager'], Manager)
        assert sub_manager.parent == manager
        assert sub_manager.get_options() == manager.get_options()

    def test_run_submanager_command(self):

        sub_manager = Manager()
        sub_manager.add_command('simple', SimpleCommand())

        manager = Manager(self.app)
        manager.add_command('sub_manager', sub_manager)

        stdout, code = run('manage.py sub_manager simple', lambda: manager.run())
        assert code == 0
        assert 'OK' in stdout

    def test_submanager_has_options(self):

        sub_manager = Manager()
        sub_manager.add_command('simple', SimpleCommand())

        manager = Manager(self.app)
        manager.add_command('sub_manager', sub_manager)
        manager.add_option('-c', '--config', dest='config', required=False)

        stdout, code = run('manage.py sub_manager simple', lambda: manager.run())
        assert code == 0
        assert 'OK' in stdout

        stdout, code = run('manage.py -c Development sub_manager simple', lambda: manager.run())
        assert code == 0
        assert 'OK' in stdout

    def test_manager_usage_with_submanager(self):

        sub_manager = Manager(usage='Example sub-manager')

        manager = Manager(self.app)
        manager.add_command('sub_manager', sub_manager)

        stdout, code = run('manage.py -h', lambda: manager.run())
        assert code == 0
        assert 'Example sub-manager' in stdout

    def test_submanager_usage(self):

        sub_manager = Manager(usage='Example sub-manager')
        sub_manager.add_command('simple', SimpleCommand())

        manager = Manager(self.app)
        manager.add_command('sub_manager', sub_manager)

        stdout, code = run('manage.py sub_manager', lambda: manager.run(),
                           capture_stderr=True)
        assert code == 2
        assert 'too few arguments' in stdout

        stdout, code = run('manage.py sub_manager -h', lambda: manager.run())
        assert code == 0
        assert 'simple command' in stdout

    def test_submanager_has_no_default_commands(self):

        sub_manager = Manager()

        manager = Manager()
        manager.add_command('sub_manager', sub_manager)

        assert 'runserver' not in sub_manager._commands
        assert 'shell' not in sub_manager._commands
