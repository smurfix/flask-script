"""
Basic idea:
# manage.py

from flaskext.script import register_script

def create_app(*args, **options):
    # *args and **kwargs are command-line options
    return Flask(__name__)

@register_script(create_app)
def do_something(name, **options):
    print name

>>> python manage.py do_something hello
... "hello"
>>> python manage.py do_something --name=hello
... "hello"

from flaskext.script import make_shell

def make_shell_ctx(app):
    return dict(db=db)

shell = make_shell(create_app, make_shell_ctx, title="My App shell")
runserver = make_runserver(create_app)

"""
