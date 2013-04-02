# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import with_statement

import os
import sys
import inspect

import argparse

from flask import Flask

from .commands import Group, Option, InvalidCommand, Command, Server, Shell
from .cli import prompt, prompt_pass, prompt_bool, prompt_choices

__all__ = ["Command", "Shell", "Server", "Manager", "Group", "Option",
           "prompt", "prompt_pass", "prompt_bool", "prompt_choices"]


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
    """

    def __init__(self, app=None, with_default_commands=None, usage=None):

        self.app = app

        self._commands = dict()
        self._options = list()

        # Primary/root Manager instance adds default commands by default,
        # Sub-Managers do not
        if with_default_commands or (app and with_default_commands is None):
            self.add_default_commands()

        self.usage = self.description = usage

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

    def create_parser(self, prog, parser=None):

        """
        Creates an ArgumentParser instance from options returned
        by get_options(), and a subparser for the given command.
        """
        prog = os.path.basename(prog)

        if parser is None:
            parser = argparse.ArgumentParser(prog=prog, usage=self.usage)

        #parser.set_defaults(func_handle=self._handle)

        for option in self.get_options():
            parser.add_argument(*option.args, **option.kwargs)

        subparsers = parser.add_subparsers()
        for name, command in self._commands.iteritems():
            description = getattr(command, 'description',
                                  'Perform command ' + name)
            p = subparsers.add_parser(name, help=description, usage=description)
            command.create_parser(name, parser=p)

        return parser

    def get_options(self):
        if self.parent:
            return self.parent._options

        return self._options

    def add_command(self, name, command):

        """
        Adds command to registry.

        :param command: Command instance
        """

        if isinstance(command, Manager):
            command.parent = self

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
        kwargs = dict(zip(*[reversed(l) for l in (args, defaults)]))

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
                                          type=unicode,
                                          required=False,
                                          default=default))

            else:
                options.append(Option(arg, type=unicode))

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

    def get_usage(self):

        """
        Returns string consisting of all commands and their
        descriptions.
        """
        pad = max(map(len, self._commands.iterkeys())) + 2
        format = '  %%- %ds%%s' % pad

        rv = []

        if self.usage:
            rv.append(self.usage)

        for name, command in sorted(self._commands.iteritems()):
            usage = name

            if isinstance(command, Manager):
                description = command.usage or ''
            else:
                description = command.description or ''

            usage = format % (name, description)
            rv.append(usage)

        return "\n".join(rv)

    def print_usage(self):

        """
        Prints result of get_usage()
        """

        print self.get_usage()

    def _handle(self, app, *args, **kwargs):
        """
        Calling manager without command prints usage message.
        """
        with app.test_request_context():
            self.print_usage()
            return 1

    def handle(self, prog, name, args=None):

        args = list(args or [])

        try:
            command = self._commands[name]
        except KeyError:
            raise InvalidCommand("Command %s not found" % name)

        app_parser = self.create_parser(prog)
        app_namespace, remaining_args = app_parser.parse_known_args([name] + args)

        kwargs = app_namespace.__dict__
        handle = kwargs['func_handle']
        del kwargs['func_handle']
        app = self.create_app(**app_namespace.__dict__)

        # get command from bounded handle function (py2.7+)
        command = handle.__self__
        if getattr(command, 'capture_all_args', False):
            positional_args = [remaining_args]
        else:
            if len(remaining_args):
                # raise correct exception
                # FIXME maybe change capture_all_args flag
                app_parser.parse_args([name] + args)
                # sys.exit(2)
            positional_args = []
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

        try:
            try:
                command = sys.argv[1]
            except IndexError:
                command = default_command

            if command is None:
                raise InvalidCommand("Please provide a command:")

            result = self.handle(sys.argv[0], command, sys.argv[2:])

            sys.exit(result or 0)

        except InvalidCommand, e:
            print e
            self.print_usage()

        sys.exit(1)
