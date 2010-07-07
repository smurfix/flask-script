# -*- coding: utf-8 -*-

import sys
import code
import getpass

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

    def prompt(self, name, default=None):
        prompt = name + (default and ' [%s]' % default or '')
        prompt += name.endswith('?') and ' ' or ': '
        while True:
            rv = raw_input(prompt)
            if rv:
                return rv
            if default is not None:
                return default

    def prompt_pass(self, name, default=None):
        prompt = name + (default and ' [%s]' % default or '')
        prompt += name.endswith('?') and ' ' or ': '
        while True:
            rv = getpass.getpass(prompt)
            if rv:
                return rv
            if default is not None:
                return default

    def prompt_bool(self, name, default=False):
        while True:
            rv = self.prompt(name + '?', default and 'Y' or 'N')
            if not rv:
                return default
            if rv.lower() in ('y', 'yes', '1', 'on', 'true', 't'):
                return True
            elif rv.lower() in ('n', 'no', '0', 'off', 'false', 'f'):
                return False

    def prompt_choices(self, name, choices, default=None):
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

    def handle(self, app, prog, name, args):

        parser = self.create_parser(prog, name)
        ns = parser.parse_args(list(args))
        
        with app.test_request_context():
            self.run(app, **ns.__dict__)

    def run(self, app):
        raise NotImplementedError


class Shell(Command):

    banner = ''
    description = 'Runs a Flask shell'
    
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
                       default=not(self.use_ipython)),)

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

    def __init__(self, app):

        if isinstance(app, Flask):
            self.app_factory = lambda: app
        else:
            self.app_factory = app
        self._commands = dict()

    def add_command(self, name, command):
        self._commands[name] = command

    def get_usage(self):
        
        rv = []

        for name, command in self._commands.iteritems():
            usage = name
            if command.description:
                usage += ": " + command.description
            rv.append(usage)

        return "\n".join(rv)
    
    def print_usage(self):
        
        print self.get_usage()

    def handle(self, prog, name, args=None):

        args = args or []

        try:
            command = self._commands[name]
        except KeyError:
            raise InvalidCommand, "Command %s not found" % name

        command.handle(self.app_factory(), prog, name, args)
    
    def run(self, commands=None):

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


