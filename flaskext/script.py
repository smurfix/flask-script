import sys
import code

from optparse import OptionParser, make_option

__all__ = ["Command", "Shell", "Server", "Manager"]

class Command(object):

    option_list = []
    help = None

    def usage(self, name):
        usage = "%s [options] %s" % (name, self.option_list)
        if self.help:
            usage += "\n\n" + self.help
        return usage

    def create_parser(self, prog, name):
        return OptionParser(prog=prog,
                            usage=self.usage(name),
                            option_list=self.option_list)

    def run(self, app):
        raise NotImplementedError


class Shell(Command):

    banner = 'Flask shell'
    help = 'Runs a Flask shell'
    
    option_list = (
        make_option('--use_ipython',
                    dest='use_ipython',
                    default=True),
    )

    def get_context(self, app):
        return dict(app=app)

    def run(self, app, use_ipython):
        context = self.get_context(app)
        if use_ipython:
            try:
                import IPython
                sh = IPython.Shell.IPShellEmbed(banner=self.banner)
                sh(global_ns=dict(), local_ns=context)
                return
            except ImportError:
                pass

        code.interact(self.banner, local=context)


class Server(Command):

    option_list = (
        make_option('-p', '--port', 
                    dest='port', 
                    type='int', 
                    default=5000),
    )

    def run(self, app, port):
        app.run(port=port)


class Manager(object):

    def __init__(self, app_factory):
        self.app_factory = app_factory
        self._commands = dict()
    
    def register(self, name, command):
        self._commands[name] = command

    def run(self):
        
        prog = sys.argv[0]

        # TBD: add help support
        try:
            name = sys.argv[1]
        except IndexError:
            print "Usage: %s [command]" % prog
            sys.exit(1)

        try:
            command = self._commands[name]
        except KeyError:
            print "Command %s not found" % name
            sys.exit(1)

        # get option list
        parser = command.create_parser(prog, name)
        options, args = parser.parse_args(sys.argv[2:])

        app = self.app_factory()
        with app.test_request_context():
            command.run(app, *args, **options.__dict__)

        sys.exit(0)
