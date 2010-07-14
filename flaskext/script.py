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
        rv = prompt(name + '?', default and 'Y' or 'N')
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
        rv = prompt(name + '? - (%s)' % ', '.join(choices), default)
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

    @property
    def description(self):
        description = self.__doc__ or ''
        return description.strip()

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


    def create_parser(self, prog):
        parser = argparse.ArgumentParser(prog=prog,
                                         description=self.description)

        for option in self.get_options():
            parser.add_argument(*option.args, **option.kwargs)   
        
        return parser

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

    def __init__(self, app, with_default_commands=True):

        """
        :param app: Flask instance or callable returning a Flask instance.
        :param with_default_commands: load commands **runserver** and **shell**
                                      by default.

        """

        self.app = app

        self._commands = dict()
        self._options = list()
        
        if with_default_commands:
            self.add_default_commands()

    def add_default_commands(self):
        """
        Adds the shell and runserver default commands. To override these 
        simply add your own equivalents using add_command or decorators.
        """

        self.add_command("shell", Shell())
        self.add_command("runserver", Server())

    def create_app(self, **kwargs):

        if isinstance(self.app, Flask):
            return self.app

        return self.app(**kwargs)

    def create_parser(self, prog):

        """
        Creates an ArgumentParser instance from options returned 
        by get_options(), and a subparser for the given command.
        """

        parser = argparse.ArgumentParser(prog=prog)
        for option in self.get_options():
            parser.add_argument(*option.args, **option.kwargs)
        
        return parser

    def get_options(self):
        return self._options

    def add_option(self, *args, **kwargs):
        """
        Adds an application-wide option. This is useful if you want to set variables
        applying to the application setup, rather than individual commands.

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
            
            > python manage.py -c dev.cfg mycommand

        Any manager options passed in the command line will not be passed to 
        the command.

        Arguments for this function are the same as for the Option class.
        """
        
        self._options.append(Option(*args, **kwargs))

    def command(self, func):
        """
        Adds a command function to the registry.
        
        :param func: command function. Should take at least one argument, the 
                     Flask application. Additional arguments depend on the 
                     options.
        
        """
            
        args, varargs, keywords, defaults = inspect.getargspec(func)
        
        options = []

        # first arg is always "app" : ignore

        args = args[1:]
        defaults = defaults or []
        kwargs = dict(zip(*[reversed(l) for l in (args, defaults)]))

        for arg in args:
            if arg in kwargs:
                
                default=kwargs[arg]

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
        
            else:
                options.append(Option(arg))


        command = Command()
        command.run = func
        command.__doc__ = func.__doc__
        command.option_list = options

        self.add_command(func.__name__, command)

        return func
    
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

    def option(self, *args, **kwargs):
        
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
            description = command.description
            if description:
                usage += ": " + description
            rv.append(usage)

        return "\n".join(rv)
    
    def print_usage(self):
        
        """
        Prints result of get_usage()
        """

        print self.get_usage()

    def handle(self, prog, name, args=None):

        args = list(args or [])

        try:
            command = self._commands[name]
        except KeyError:
            raise InvalidCommand, "Command %s not found" % name

        help_args = ('-h', '--help')

        # remove -h from args if present, and add to remaining args
        app_args = [a for a in args if a not in help_args]

        app_parser = self.create_parser(prog)
        app_namespace, remaining_args = app_parser.parse_known_args(app_args)

        for arg in help_args:
            if arg in args:
                remaining_args.append(arg)

        command_parser = command.create_parser(prog)
        command_namespace = command_parser.parse_args(remaining_args)
        
        app = self.create_app(**app_namespace.__dict__)

        with app.test_request_context():
            command.run(app, **command_namespace.__dict__)
        
    def run(self, commands=None):
        
        """
        Prepares manager to receive command line input. Usually run
        inside "if __name__ == "__main__" block in a Python script.

        :param commands: optional dict of commands. Appended to any commands 
                         added using add_command().
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


