Flask-Script
======================================

.. module:: Flask-Script

The **Flask-Script** extension provides support for writing external scripts in Flask.

You define and register commands that can be called from the command line::

    # manage.py
    
    from flaskext.script import Manager

    from myapp import create_app

    class PrintCommand(Command):
        def run(self):
            print "hello"

    manager = Manager(create_app)
    manager.register("print", PrintCommand())

    if __name__ == "__main__":
        manager.run()

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

The next step is to create and register your commands. First you need to subclass the ``Command`` class.
You then need, at the very least, to define a ``run`` method for this class.

To take a very simple example, we want to create a ``Print`` command that just prints out "hello world". It 
doesn't take any arguments so is very straightforward::

    from flaskext.script import Command

    class Print(Command):

        help = "prints hello world"

        def run(self, app):
            print "hello world"

Now the command needs to be registered with our ``Manager`` instance, created above::

    manager.register('print', Print())

This of course needs to be called before ``manager.run``. Now in our command line::

    >>> python manage.py print
    ... "hello world"

The first argument to your ``run`` command, other than ``self``, is always ``app``: this is the Flask
application instance provided by the ``app_factory`` passed to the ``Manager``. Additional arguments
are configured through the ``option_list`` (see below).

Notice also the ``help`` attribute. If you type the following::

    >>> python manage.py help print
    ... "prints hello world"

Typing "help" before a command will display the ``help`` attribute of that command. If you just type::

    >>> python manage.py help

You get a list of registered commands.

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

    from optparse import make_option
    from flaskext.script import Command, Manager

    class Print(Command):

        option_list = (
            make_option('--name', '-n', dest='name'),
        )

        def run(self, app, name):
            print "hello %s" % name

Options must be created using the ``make_option`` function from the `optparse <http://docs.python.org/library/optparse.html>`_ 
library.

Default commands
----------------

**Flask-Script** has a couple of ready commands you can register and customize (in addition to the ``help`` command): ``Server``
and ``Shell``.

The ``Server`` command runs the **Flask** development server. It takes an optional ``port`` argument (default **5000**)::

    from flaskext.script import Server, Manager
    from myapp import create_app

    manager = Manager(create_app)
    manager.register("runserver", Server())

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
    manager.register("shell", Shell(make_context=_make_context))
    
This is handy if you want to include a bunch of defaults in your shell to save typing lots of ``import`` statements.

The ``Shell`` command will use `IPython <http://ipython.scipy.org/moin/>`_ if it is installed, otherwise it defaults to the standard Python shell. You can disable this behaviour in two ways: by passing the ``use_ipython`` argument to the ``Shell`` constructor, or passing the flag ``--no-ipython`` in the command line. 

API
---

.. module:: flaskext.script

.. _Flask: http://flask.pocoo.org
.. _Bitbucket: http://bitbucket.org/danjac/Flask-Script
