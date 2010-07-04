import sys
import code

from flask import current_app

from optparse import OptionParser, make_option

class Command(object):

    def __init__(self, func, name, usage, options):
        self.func = func
        self.name = name
        self.options = options or []
        self.usage = usage

    def create_parser(self, prog):

        parser = OptionParser(prog=prog,
                              usage=self.usage)


        parser.add_options(self.options)

        return parser

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Manager(object):

    def __init__(self, app_factory):
        self.app_factory = app_factory
        self._commands = dict()
        
        server_options = [make_option('-p', '--port', default=5000, type="int")]
        @self.register('runserver', options=server_options)
        def runserver(port):
            current_app.run(port=port)


    def configure_shell(self, make_context=None, title=''):

        pass
    
    def register(self, name=None, usage=None, options=None):
        def decorator(f):
            self._commands[name or f.__name__] = \
                Command(f, name, usage, options)
        return decorator

    def usage(self):

        return "\n\r".join(sorted(self._commands.keys()))

    def run(self):
        
        try:
            command = self._commands[sys.argv[1]]
        except (IndexError, KeyError):
            print self.usage()
            sys.exit(1)

        # get option list
        parser = command.create_parser(sys.argv[0])
        options, args = parser.parse_args(sys.argv[2:])

        app = self.app_factory()
        with app.test_request_context():
            command(*args, **options.__dict__)

        sys.exit(0)
