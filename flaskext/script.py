# -*- coding: utf-8 -*-

import sys
import code
import getpass
import inspect
import warnings

import argparse

from flask import Flask

__all__ = ["Command", "Shell", "Server", "Manager", "Option",
           "prompt", "prompt_pass", "prompt_bool", "prompt_choices"]

def prompt(name, default=None):
    
    """
    Grab user input from command line.

    :param name: prompt text
    :param default: default value if no input provided.
    """

    prompt = name + (default and ' [%s]' % default or '')
    prompt += name.endswith('?') and ' ' or ': '
    while True:
        rv = raw_input(prompt)
        if rv:
            return rv
        if default is not None:
            return default


def prompt_pass(name, default=None):

    """
    Grabs hidden (password) input from command line.

    :param name: prompt text
    :param default: default value if no input provided.
    """

    prompt = name + (default and ' [%s]' % default or '')
    prompt += name.endswith('?') and ' ' or ': '
    while True:
        rv = getpass.getpass(prompt)
        if rv:
            return rv
        if default is not None:
            return default


def prompt_bool(name, default=False):
    
    """
    Grabs user input from command line and converts to boolean
    value.

    :param name: prompt text
    :param default: default value if no input provided.
    """
    
    while True:
        rv = self.prompt(name + '?', default and 'Y' or 'N')
        if not rv:
            return default
        if rv.lower() in ('y', 'yes', '1', 'on', 'true', 't'):
            return True
        elif rv.lower() in ('n', 'no', '0', 'off', 'false', 'f'):
            return False


def prompt_choices(name, choices, default=None):
    
    """
    Grabs user input from command line from set of provided choices.

    :param name: prompt text
    :param choices: list or tuple of available choices
    :param default: default value if no input provided.
    """

    if default is None:
        default = choices[0]
    while True:
        rv = self.prompt(name + '? - (%s)' % ', '.join(choices), default)
        rv = rv.lower()
        if not rv:
            return default
        if rv in choices:
            if rv == 'none':
                return None
            else:
                return rv


class Option(object):

    """
    Stores positional and optional arguments for ArgumentParser.
    """
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Command(object):
    
    """
    Base class for creating commands.
    """

    option_list = []

    def create_parser(self, prog, name):

        """
        Creates an ArgumentParser instance from options returned 
        by get_options()
        """

        description = self.__doc__ or ''

        parser = argparse.ArgumentParser(prog=prog, 
                                         description=description)
        for option in self.get_options():
            parser.add_argument(*option.args, **option.kwargs)
        return parser

    def add_option(self, option):
        
        """
        Adds option to option list.
        """
        
        self.option_list.append(option)

    def get_options(self):

        """
        By default, returns self.option_list.Override if you
        need to do instance-specific configuration.
        """

        return self.option_list

    def handle(self, app, prog, name, args):

        parser = self.create_parser(prog, name)
        ns = parser.parse_args(list(args))
        
        with app.test_request_context():
            self.run(app, **ns.__dict__)

    def run(self, app):

        """
        Runs a command. This must be implemented by the subclass. The first
        argument is always the app (Flask instance) followed by arguments
        as configured by the Command options.
        """

        raise NotImplementedError

    def prompt(self, name, default=None):
        warnings.warn_explicit(
            "Command.prompt is deprecated, use prompt() function instead")

        prompt(name, default)

    def prompt_pass(self, name, default=None):
        warnings.warn_explicit(
            "Command.prompt_pass is deprecated, use prompt_pass() function instead")

        prompt_pass(name, default)

    def prompt_bool(self, name, default=False):
        warnings.warn_explicit(
            "Command.prompt_bool is deprecated, use prompt_bool() function instead")

        prompt_bool(name, default)

    def prompt_choices(self, name, choices, default=None):
        warnings.warn_explicit(
            "Command.choices is deprecated, use prompt_choices() function instead")

        prompt_choices(name, choices, default)

class Shell(Command):

    "Runs a Python shell inside Flask application context."

    banner = ''
    
    def __init__(self, banner=None, make_context=None, use_ipython=True):

        """
        :param banner: banner appearing at top of shell when started
        :param make_context: a callable returning a dict of variables 
        used in the shell namespace. The callable takes a single argument,
        "app", the Flask instance. By default returns a dict consisting
        of just the app.
        :param use_ipython: use IPython shell if available, ignore if not.
        The IPython shell can be turned off in command line by passing the
        --no-ipython flag.
        """

        self.banner = banner or self.banner
        self.use_ipython = use_ipython

        if make_context is None:
            make_context = lambda app: dict(app=app)

        self.make_context = make_context

    def get_options(self):

        return (
                Option('--no-ipython',
                       action="store_true",
                       dest='no_ipython',
                       default=not(self.use_ipython)),)

    def get_context(self, app):
        
        """
        Returns a dict of context variables added to the shell namespace.
        """

        return self.make_context(app)

    def run(self, app, no_ipython):

        """
        Runs the shell. Unless no_ipython is True or use_python is False
        then runs IPython shell if that is installed.
        """

        context = self.get_context(app)
        if not no_ipython:
            try:
                import IPython
                sh = IPython.Shell.IPShellEmbed(banner=self.banner)
                sh(global_ns=dict(), local_ns=context)
                return
            except ImportError:
                pass

        code.interact(self.banner, local=context)


class Server(Command):

    "Runs the Flask development server i.e. app.run()"

    def __init__(self, host='127.0.0.1', port=5000, use_debugger=True,
        use_reloader=True):

        """
        :param host: server host
        :param port: server port
        :param use_debugger: if False, will no longer use Werkzeug debugger.
        This can be overriden in the command line by passing the -d flag.
        :param use_reloader: if Flase, will no loner use auto-reloader.
        This can be overriden in the command line by passing the -r flag.
        """

        self.port = port
        self.host = host
        self.use_debugger = use_debugger
        self.use_reloader = use_reloader
    
    def get_options(self):

        return (
                Option('-t', '--host',
                       dest='host',
                       default=self.host),

                Option('-p', '--port', 
                       dest='port', 
                       type=int,
                       default=self.port),

                Option('-d', '--debug',
                       action='store_true',
                       dest='use_debugger',
                       default=self.use_debugger),
        
                Option('-r', '--reload',
                       action='store_true',
                       dest='use_reloader',
                       default=self.use_reloader))

    def run(self, app, host, port, use_debugger, use_reloader):
        app.run(host=host,
                port=port,
                debug=use_debugger,
                use_debugger=use_debugger,
                use_reloader=use_reloader)


class InvalidCommand(Exception):
    pass


class Manager(object):

    """
    Controller class for handling a set of commands.

    Typical usage::
        
        class Print(Command):

            def run(self, app):
                print "hello"

        app = Flask(__name__)
        
        manager = Manager(app)
        manager.add_command("print", Print())
        
        if __name__ == "__main__":
            manager.run()

    On command line::

        python manage.py print
        > hello

    """

    def __init__(self, app):

        """
        :param app: Flask instance or callable returning a Flask instance.
        """

        if isinstance(app, Flask):
            self.app_factory = lambda: app
        else:
            self.app_factory = app
        self._commands = dict()

    def command(self, func):
        """
        Adds a command function to the registry.
        
        :param func: command function. Should take at least one argument, the 
        Flask application. Additional arguments depend on the options.
        
        """
            
        args, varargs, keywords, defaults = inspect.getargspec(func)
        
        options = []

        # first arg is always "app" : ignore

        args = args[1:]
        defaults = defaults or []
        args.reverse()

        for counter, arg in enumerate(args):
            try:
                default=defaults[counter]
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
                                          required=False,
                                          default=default))
        
            except IndexError:
                options.append(Option(arg))
        
        options.reverse()

        # add optional options

        class _Command(Command):

            def run(self, app, *args, **kwargs):
                func(app, *args, **kwargs)

        command = _Command()
        command.__doc__ = func.__doc__
        command.option_list = options

        self.add_command(func.__name__, command)

        return func


    def option(self, *args, **kwargs):
        
        option = Option(*args, **kwargs)

        def decorate(func):
            name = func.__name__
            
            if name not in self._commands:

                class _Command(Command):

                    def run(self, app, *args, **kwargs):
                        func(app, *args, **kwargs)
            
                command = _Command()
                command.__doc__ = func.__doc__
                command.option_list = []
                self.add_command(name, command)

            self._commands[name].option_list.append(option)
            return func
        return decorate

    def add_command(self, name, command):

        """
        Adds command to registry.

        :param command: Command instance
        """

        self._commands[name] = command

    def get_usage(self):
        
        """
        Returns string consisting of all commands and their
        descriptions.
        """

        rv = []

        for name, command in self._commands.iteritems():
            usage = name
            if hasattr(command, 'description'):
                warnings.warn_explicit(
                    "description is deprecated, use docstrings instead")
                usage += ": " + command.description
            elif command.__doc__:
                usage += ": " + command.__doc__
            rv.append(usage)

        return "\n".join(rv)
    
    def print_usage(self):
        
        """
        Prints result of get_usage()
        """

        print self.get_usage()

    def handle(self, prog, name, args=None):

        args = args or []

        try:
            command = self._commands[name]
        except KeyError:
            raise InvalidCommand, "Command %s not found" % name

        command.handle(self.app_factory(), prog, name, args)
    
    def run(self, commands=None):
        
        """
        Prepares manager to receive command line input. Usually run
        inside "if __name__ == "__main__" block in a Python script.

        :param commands: optional dict of commands. Appended to any
        commands added using add_command().
        """

        if commands:
            self._commands.update(commands)
        
        try:
            self.handle(sys.argv[0],
                        sys.argv[1],
                        sys.argv[2:])
            
            sys.exit(0)

        except IndexError:
            self.print_usage()
            sys.exit(0)
        
        except InvalidCommand, e:
            print e
            self.print_usage()

        sys.exit(1)


