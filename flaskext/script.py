import sys
import code

import argparse

from flask import Flask

__all__ = ["Command", "Shell", "Server", "Manager", "Option"]

class Option(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class Command(object):

    option_list = []
    description = None

    def create_parser(self, prog, name):

        parser = argparse.ArgumentParser(prog=prog, 
                                         description=self.description)
        for option in self.get_options():
            parser.add_argument(*option.args, **option.kwargs)
        return parser

    def add_option(self, option):
        self.option_list.append(option)

    def get_options(self):
        """
        By default, returns self.option_list.Override if you
        need to do instance-specific configuration.
        """

        return self.option_list

    def run(self, app):
        raise NotImplementedError


class Help(Command):
    
    def __init__(self, manager):
        
        self.manager = manager
        
    def run(self, app):

        self.manager.print_usage()


class Shell(Command):

    banner = ''
    description = 'Runs a Flask shell'
    
    option_list = (
        Option('--no-ipython',
               action="store_true",
               dest='no_ipython',
               default=False),
    )

    
    def __init__(self, banner=None, make_context=None, use_ipython=True):

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
                       default=not(self.use_ipython)))

    def get_context(self, app):
        return self.make_context(app)

    def run(self, app, no_ipython):
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

    description = "Runs Flask development server"

    def __init__(self, host='127.0.0.1', port=5000, use_debugger=True,
        use_reloader=True):

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
                use_debugger=use_debugger,
                use_reloader=use_reloader)


class InvalidCommand(Exception):
    pass

class Manager(object):

    help_class = Help

    def __init__(self, app):

        if isinstance(app, Flask):
            self.app_factory = lambda: app
        else:
            self.app_factory = app
        self._commands = dict()
        
        self.add_command("help", self.help_class(self))

    def add_command(self, name, command):
        self._commands[name] = command

    def print_usage(self):
        
        commands = [k for k in sorted(self._commands)]
        usage = "\n".join(commands)
        print usage

    def run_command(self, prog, name, *args):

        app = self.app_factory()

        try:
            command = self._commands[name]
        except KeyError:
            raise InvalidCommand, "Command %s not found" % name

        parser = command.create_parser(prog, name)
        
        ns = parser.parse_args(list(args))
        
        with app.test_request_context():
            command.run(app, **ns.__dict__)
    
    def run(self):
        
        try:
            self.run_command(sys.argv[0],
                             sys.argv[1],
                             *sys.argv[2:])
            sys.exit(0)

        except IndexError:
            print "No command provided"
            self.print_usage()
        
        except InvalidCommand, e:
            print e
            self.print_usage()

        sys.exit(1)


