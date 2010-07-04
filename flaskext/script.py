"""
Basic idea:
# manage.py

from flaskext.script import Manager

def create_app(config=None, *args, **options):
    # *args and **kwargs are command-line options
    app = Flask(__name__)
    if config is not None:
        app.config.from_object(config)
    return app

manager = Manager(create_app)

@manager.register('do_something')
def do_something(name, **options):
    print name

>>> python manage.py do_something hello
... "hello"
>>> python manage.py do_something --name=hello
... "hello"


def make_shell_ctx(app):
    return dict(db=db, app=app)

manager.configure_shell(ctx=make_shell_ctx, title="My App Context")

if __name__ == "__main__":
    manager.run()

"""
import sys
import code

from optparse import OptionParser, make_option

class Manager(object):

    def __init__(self, app_factory):
        self.app_factory = app_factory
        self._scripts = dict()
    
    def register(self, name=None):
        def decorator(f):
            self._scripts[name or f.__name__] = f
            print self._scripts
            f.option_list = getattr(f, 'option_list', [])
        return decorator

    def usage(self, script):
        return "ok"

    def create_parser(self, name, script):
        return OptionParser(prog=name,
                            usage=self.usage(script),
                            option_list=script.option_list)
    def run(self):

        try:
            script = self._scripts[sys.argv[1]]
        except KeyError:
            print "Command %s not found" % script
            return

        # get option list
        parser = self.create_parser(sys.argv[0], script)
        options, args = parser.parse_args(sys.argv[2:])
        app = self.app_factory()
        with app.test_request_context():
            script(*args, **options.__dict__)
