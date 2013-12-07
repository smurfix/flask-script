# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import re
import sys
import inspect
import warnings

import argparse

from flask import Flask

from ._compat import text_type, iteritems, imap, izip
from .commands import Group, Option, InvalidCommand, Command, Server, Shell
from .cli import prompt, prompt_pass, prompt_bool, prompt_choices

__all__ = ["Command", "Shell", "Server", "Manager", "Group", "Option",
           "prompt", "prompt_pass", "prompt_bool", "prompt_choices"]

safe_actions = (argparse._StoreAction,
                argparse._StoreConstAction,
                argparse._StoreTrueAction,
                argparse._StoreFalseAction,
                argparse._AppendAction,
                argparse._AppendConstAction,
                argparse._CountAction)


try:
    import argcomplete
    ARGCOMPLETE_IMPORTED = True
except ImportError:
    ARGCOMPLETE_IMPORTED = False


class Manager(object):
    """
    Controller class for handling a set of commands.

    Typical usage::

        class Print(Command):

            def run(self):
                print "hello"

        app = Flask(__name__)

        manager = Manager(app)
        manager.add_command("print", Print())

        if __name__ == "__main__":
            manager.run()

    On command line::

        python manage.py print
        > hello

    :param app: Flask instance or callable returning a Flask instance.
    :param with_default_commands: load commands **runserver** and **shell**
                                  by default.
    :param disable_argcomplete: disable automatic loading of argcomplete.

    """

    def __init__(self, app=None, with_default_commands=None, usage=None,
                 help=None, description=None, disable_argcomplete=False):

        self.app = app

        self._commands = dict()
        self._options = list()

        # Primary/root Manager instance adds default commands by default,
        # Sub-Managers do not
        if with_default_commands or (app and with_default_commands is None):
            self.add_default_commands()

        self.usage = usage
        self.help = help if help is not None else usage
        self.description = description if description is not None else usage
        self.disable_argcomplete = disable_argcomplete

        self.parent = None

    def add_default_commands(self):
        """
        Adds the shell and runserver default commands. To override these
        simply add your own equivalents using add_command or decorators.
        """

        self.add_command("shell", Shell())
        self.add_command("runserver", Server())

    def add_option(self, *args, **kwargs):
        """
        Adds an application-wide option. This is useful if you want to set
        variables applying to the application setup, rather than individual
        commands.

        For this to work, the manager must be initialized with a factory
        function rather than an instance. Otherwise any options you set will
        be ignored.

        The arguments are then passed to your function, e.g.::

            def create_app(config=None):
                app = Flask(__name__)
                if config:
                    app.config.from_pyfile(config)

                return app

            manager = Manager(create_app)
            manager.add_option("-c", "--config", dest="config", required=False)

        and are evoked like this::

            > python manage.py -c dev.cfg mycommand

        Any manager options passed in the command line will not be passed to
        the command.

        Arguments for this function are the same as for the Option class.
        """

        self._options.append(Option(*args, **kwargs))

    def create_app(self, **kwargs):
        if self.parent:
            # Sub-manager, defer to parent Manager
            return self.parent.create_app(**kwargs)

        if isinstance(self.app, Flask):
            return self.app

        return self.app(**kwargs)

    def create_parser(self, prog, parents=None):
        """
        Creates an ArgumentParser instance from options returned
        by get_options(), and a subparser for the given command.
        """
        prog = os.path.basename(prog)

        options_parser = argparse.ArgumentParser(add_help=False)
        for option in self.get_options():
            options_parser.add_argument(*option.args, **option.kwargs)

        # parser_parents = parents if parents else [option_parser]
        # parser_parents = [options_parser]

        parser = argparse.ArgumentParser(prog=prog, usage=self.usage,
                                         description=self.description,
                                         parents=[options_parser])

        subparsers = parser.add_subparsers()

        for name, command in self._commands.items():
            usage = getattr(command, 'usage', None)
            help = getattr(command, 'help', command.__doc__)
            description = getattr(command, 'description', command.__doc__)

            # Only pass `parents` argument for commands that support it
            try:
                command_parser = command.create_parser(name, parents=[options_parser])
            except TypeError:
                warnings.warn("create_parser for {0} command should accept a `parents` argument".format(name), DeprecationWarning)
                command_parser = command.create_parser(name)

            subparser = subparsers.add_parser(name, usage=usage, help=help,
                                              description=description,
                                              parents=[command_parser], add_help=False)


        ## enable autocomplete only for parent parser when argcomplete is
        ## imported and it is NOT disabled in constructor
        if parents is None and ARGCOMPLETE_IMPORTED \
                and not self.disable_argcomplete:
            argcomplete.autocomplete(parser, always_complete_options=True)

        return parser

    # def foo(self, app, *args, **kwargs):
    #     print(args)

    def get_options(self):
        if self.parent:
            return self.parent._options

        return self._options

    def add_command(self, *args, **kwargs):
        """
        Adds command to registry.

        :param command: Command instance
        :param name: Name of the command (optional)
        :param namespace: Namespace of the command (optional; pass as kwarg)
        """

        if len(args) == 1:
            command = args[0]
            name = None

        else:
            name, command = args

        if name is None:
            if hasattr(command, 'name'):
                name = command.name

            else:
                name = type(command).__name__.lower()
                name = re.sub(r'command$', '', name)

        if isinstance(command, Manager):
            command.parent = self

        if isinstance(command, type):
            command = command()

        namespace = kwargs.get('namespace')
        if not namespace:
            namespace = getattr(command, 'namespace', None)

        if namespace:
            if namespace not in self._commands:
                self.add_command(namespace, Manager())

            self._commands[namespace]._commands[name] = command

        else:
            self._commands[name] = command

    def command(self, func):
        """
        Decorator to add a command function to the registry.

        :param func: command function.Arguments depend on the
                     options.

        """

        args, varargs, keywords, defaults = inspect.getargspec(func)

        options = []

        # first arg is always "app" : ignore

        defaults = defaults or []
        kwargs = dict(izip(*[reversed(l) for l in (args, defaults)]))

        for arg in args:

            if arg in kwargs:

                default = kwargs[arg]

                if isinstance(default, bool):
                    options.append(Option('-%s' % arg[0],
                                          '--%s' % arg,
                                          action="store_true",
                                          dest=arg,
                                          required=False,
                                          default=default))
                else:
                    options.append(Option('-%s' % arg[0],
                                          '--%s' % arg,
                                          dest=arg,
                                          type=text_type,
                                          required=False,
                                          default=default))

            else:
                options.append(Option(arg, type=text_type))

        command = Command()
        command.run = func
        command.__doc__ = func.__doc__
        command.option_list = options

        self.add_command(func.__name__, command)

        return func

    def option(self, *args, **kwargs):
        """
        Decorator to add an option to a function. Automatically registers the
        function - do not use together with ``@command``. You can add as many
        ``@option`` calls as you like, for example::

            @option('-n', '--name', dest='name')
            @option('-u', '--url', dest='url')
            def hello(name, url):
                print "hello", name, url

        Takes the same arguments as the ``Option`` constructor.
        """

        option = Option(*args, **kwargs)

        def decorate(func):
            name = func.__name__

            if name not in self._commands:

                command = Command()
                command.run = func
                command.__doc__ = func.__doc__
                command.option_list = []

                self.add_command(name, command)

            self._commands[name].option_list.append(option)
            return func
        return decorate

    def shell(self, func):
        """
        Decorator that wraps function in shell command. This is equivalent to::

            def _make_context(app):
                return dict(app=app)

            manager.add_command("shell", Shell(make_context=_make_context))

        The decorated function should take a single "app" argument, and return
        a dict.

        For more sophisticated usage use the Shell class.
        """

        self.add_command('shell', Shell(make_context=func))

        return func

    def handle(self, prog, args=None):

        app_parser = self.create_parser(prog)

        if args is None or len(args) == 0:
            app_parser.print_help()
            return 2

        args = list(args or [])
        app_namespace, remaining_args = app_parser.parse_known_args(args)

        # get the handle function and remove it from parsed options
        kwargs = app_namespace.__dict__
        handle = kwargs.pop('func_handle', None)
        if not handle:
            app_parser.error('too few arguments')

        # get only safe config options
        app_config_keys = [action.dest for action in app_parser._actions
                           if action.__class__ in safe_actions]

        # pass only safe app config keys
        app_config = dict((k, v) for k, v in iteritems(kwargs)
                          if k in app_config_keys)

        # remove application config keys from handle kwargs
        kwargs = dict((k, v) for k, v in iteritems(kwargs)
                      if k not in app_config_keys)

        # get command from bound handle function (py2.7+)
        command = handle.__self__
        if getattr(command, 'capture_all_args', False):
            positional_args = [remaining_args]
        else:
            if len(remaining_args):
                # raise correct exception
                # FIXME maybe change capture_all_args flag
                app_parser.parse_args(args)
                # sys.exit(2)
                pass
            positional_args = []

        app = self.create_app(**app_config)

        return handle(app, *positional_args, **kwargs)

    def run(self, commands=None, default_command=None):
        """
        Prepares manager to receive command line input. Usually run
        inside "if __name__ == "__main__" block in a Python script.

        :param commands: optional dict of commands. Appended to any commands
                         added using add_command().

        :param default_command: name of default command to run if no
                                arguments passed.
        """

        if commands:
            self._commands.update(commands)

        if default_command is not None and len(sys.argv) == 1:
            sys.argv.append(default_command)

        try:
            result = self.handle(sys.argv[0], sys.argv[1:])
        except SystemExit as e:
            result = e.code

        sys.exit(result or 0)
