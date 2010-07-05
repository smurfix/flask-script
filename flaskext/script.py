import sys
import code

import argparse

from flask import Flask

__all__ = ["Command", "Shell", "Server", "Manager"]

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
        for option in self.option_list:
            parser.add_argument(*option.args, **option.kwargs)
        return parser

    def run(self, app):
        raise NotImplementedError


class Help(Command):
    
    def __init__(self, manager):
        
        self.manager = manager
        
    def run(self, app, command=None):
    
        if command:
            try:
                command = self.manager._commands[command]
                print command.help
                return
            except KeyError:
                print "Command %s not found in list:\n" % command

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

    def get_context(self, app):
        return self.make_context(app)

    def run(self, app, no_ipython):
        context = self.get_context(app)
        if self.use_ipython and not no_ipython:
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

    option_list = (
        Option('-p', '--port', 
               dest='port', 
               type=int, 
               default=5000),
    )

    def run(self, app, port):
        app.run(port=port)


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
        
        self.register("help", self.help_class(self))

    def register(self, name, command):
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


