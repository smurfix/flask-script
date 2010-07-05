Flask-Script
======================================

.. module:: Flask-Script

The **Flask-Script** extension provides support for writing external scripts in Flask. It uses `argparse`_ to parse command line arguments.

You define and add commands that can be called from the command line to a ``Manager`` instance::

    # manage.py
    
    from flaskext.script import Manager

    from myapp import create_app

    class Print(Command):
        def run(self):
            print "hello"

    manager = Manager(create_app)
    manager.add_command("print", Print())

    if __name__ == "__main__":
        manager.run()

Then run the script like this::

    >>> python manage.py print
    ... "hello"
    
Source code and issue tracking at `Bitbucket`_.

Installing Flask-Script
------------------------

Install with **pip** and **easy_install**::

    pip install Flask-Script

or download the latest version from Bitbucket::

    hg clone http://bitbucket.org/danjac/flask-script

    cd flask-script

    python setup.py develop

If you are using **virtualenv**, it is assumed that you are installing **Flask-Script**
in the same virtualenv as your Flask application(s).

Creating and running commands
-----------------------------

The first step is to create a Python module to run your script commands in. You can call it
anything you like, for our examples we'll call it **manage.py**.

You don't have to place all your commands in the same file; for example, in a larger project
with lots of commands you might want to split them into a number of files with related commands.

In your **manage.py** file you have to create a ``Manager`` instance. The ``Manager`` class
keeps track of all the commands and handles how they are called from the command line::

    from flaskext.script import Manager

    app = Flask(__name__)
    # configure your app

    manager = Manager(app)

    if __name__ == "__main__":
        manager.run()

Calling ``manager.run()`` prepares your ``Manager`` instance to receive input from the command line.

The ``Manager`` requires a single argument, a **Flask** instance. This may also be a function or callable
that returns a **Flask** instance instead, if you want to use a factory pattern.

The next step is to create and add your commands. First you need to subclass the ``Command`` class.
You then need, at the very least, to define a ``run`` method for this class.

To take a very simple example, we want to create a ``Print`` command that just prints out "hello world". It 
doesn't take any arguments so is very straightforward::

    from flaskext.script import Command

    class Print(Command):

        description = "prints hello world"

        def run(self, app):
            print "hello world"

Now the command needs to be add_commanded with our ``Manager`` instance, created above::

    manager.add_command('print', Print())

This of course needs to be called before ``manager.run``. Now in our command line::

    >>> python manage.py print
    ... "hello world"

The first argument to your ``run`` command, other than ``self``, is always ``app``: this is the Flask
application instance provided by the ``app`` passed to the ``Manager``. Additional arguments
are configured through the ``option_list`` (see below).

To get a list of available commands and their descriptions, just run with no command::

    >>> python manage.py

To get help text for a particular command::

    >>> python manage.py runserver -h

This will print usage plus the ``description`` of the ``Command``.

Adding arguments to commands
----------------------------

Most commands take a number of named or positional arguments that you pass in the command line.

Taking the above example, rather than just print "hello world" we would like to be able to print some
arbitrary name, like this::

    >>> python manage.py print --name=Joe
    ... "hello Joe"

or alternatively:

    >>> python manage.py print -n Joe

To facilitate this you use the ``option_list`` attribute of the ``Command`` class::

    from flaskext.script import Command, Manager, Option

    class Print(Command):

        option_list = (
            Option('--name', '-n', dest='name'),
        )

        def run(self, app, name):
            print "hello %s" % name

Options are provided as ``Option`` instances. The ``Option`` takes exactly the same arguments as `argparse.ArgumentParser.add_argument <http://argparse.googlecode.com/svn/trunk/doc/add_argument.html>`_.

Alternatively, you can define a ``get_options`` method for your ``Command`` class. This is useful if you want to be able
to return options at runtime based on for example per-instance attributes::

    class Print(Command):

        def __init__(self, default_name='Joe'):
            self.default_name=default_name

        def get_options(self):
            return [
                Option('--name', '-n', dest='name', default=self.default_name),
            ]

        def run(self, app, name):
            print "hello %s" % name

Default commands
----------------

**Flask-Script** has a couple of ready commands you can add_command and customize (in addition to the ``help`` command): ``Server``
and ``Shell``.

The ``Server`` command runs the **Flask** development server. It takes an optional ``port`` argument (default **5000**)::

    from flaskext.script import Server, Manager
    from myapp import create_app

    manager = Manager(create_app)
    manager.add_command("runserver", Server())

    if __name__ == "__main__":
        manager.run()

and then run as so:

    >>> python manage.py runserver

Needless to say the development server is not intended for production use.

The ``Shell`` command starts a Python shell. You can pass in a ``make_context`` argument, which must be a ``callable`` returning a ``dict``. By default, this is just a dict returning the ``app`` instance::

    from flaskext.script import Shell, Manager
    
    from myapp import app
    from myapp import models
    from myapp.models import db

    def _make_context(app):
        return dict(app=app, db=db, models=models)

    manager = Manager(create_app)
    manager.add_command("shell", Shell(make_context=_make_context))
    
This is handy if you want to include a bunch of defaults in your shell to save typing lots of ``import`` statements.

The ``Shell`` command will use `IPython <http://ipython.scipy.org/moin/>`_ if it is installed, otherwise it defaults to the standard Python shell. You can disable this behaviour in two ways: by passing the ``use_ipython`` argument to the ``Shell`` constructor, or passing the flag ``--no-ipython`` in the command line. 

API
---

.. module:: flaskext.script

.. class:: Manager
    
    Manages a set of commands.

    .. method:: __init__(app)

        :param app: **Flask** application instance or callable that returns a **Flask** application.

    .. method:: run()

    Run a command based on command-line inputs. Typically you would call this inside a ``if __name__ == "__main__"`` block.

.. class:: Command

    Base class for creating new commands.

    .. attribute:: description

    Description added to help text.

    .. attribute:: option_list

    List of options passed to argument parser. Each item must be an ``Option`` instance.

    .. method:: get_options()

    Returns list of ``Option`` instances. By default just returns ``option_list``. This is useful if you need to do per-instance configuration. 

    .. method:: run(app)

    Runs the command. This must be defined or ``NotImplementedError`` is raised. Takes at least one argument, ``app``, plus any specific positional or optional arguments required by the command.

    
    :param app: Flask application instance

.. class:: Shell

    Command to start a Python shell.

    .. method:: __init__(banner='', make_context=None)

        :param banner: banner appearing in shell when started.
        :param make_context: a function that must return a ``dict``. If you wish to add any context variables to your shell namespace, then add them here. The ``make_context`` function takes one argument, ``app``. By default the ``app`` instance is passed to the shell.

.. class:: Server

    Command to start the Flask development server.

.. class:: Option

    Stores option parameters for ``argparse.add_argument``. Use with ``Command.option_list``.

.. _Flask: http://flask.pocoo.org
.. _Bitbucket: http://bitbucket.org/danjac/Flask-Script
.. _argparse: http://pypi.python.org/pypi/argparse
