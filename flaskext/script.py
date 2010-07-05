import sys
import code

from optparse import OptionParser, make_option

__all__ = ["Command", "Shell", "Server", "Manager"]

class Command(object):

    option_list = []
    help = None

    def usage(self, name):
        usage = "%s [options] %s" % (name, self.option_list or '')
        if self.help:
            usage += "\n\n" + self.help
        return usage

    def create_parser(self, prog, name):
        return OptionParser(prog=prog,
                            usage=self.usage(name),
                            option_list=self.option_list)

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

    banner = 'Flask shell'
    help = 'Runs a Flask shell'
    
    option_list = (
        make_option('--use-ipython',
                    dest='use_ipython',
                    type='choice',
                    choices=("yes", "no"),
                    default="yes"),
    )

    
    def __init__(self, banner=None, make_context=None, use_ipython=True):

        self.banner = banner or self.banner
        self.use_ipython = use_ipython

        if make_context is None:
            make_context = lambda app: dict(app=app)

        self.make_context = make_context

    def get_context(self, app):
        return self.make_context(app)

    def run(self, app, use_ipython):
        context = self.get_context(app)
        if self.use_ipython and use_ipython == "yes":
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

    help_class = Help

    def __init__(self, app_factory):
        self.app_factory = app_factory
        self._commands = dict()
        
        self.register("help", self.help_class(self))

    def register(self, name, command):
        self._commands[name] = command

    def print_usage(self):
        
        commands = [self._commands[k].usage(k) for k in sorted(self._commands)]
        usage = "\n".join(commands)
        print usage

    def run(self):
        
        prog = sys.argv[0]

        try:
            name = sys.argv[1]
            command = self._commands[name]
        except (IndexError, KeyError):
            name = "help"
            command = self._commands[name]

        parser = command.create_parser(prog, name)
        options, args = parser.parse_args(sys.argv[2:])
        kwargs = options.__dict__

        app = self.app_factory()

        with app.test_request_context():
            command.run(app, *args, **kwargs)

        sys.exit(0)
