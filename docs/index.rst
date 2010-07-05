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

    from myapp import create_app

    manager = Manager(app_factory=create_app)

    if __name__ == "__main__":
        manager.run()

Calling ``manager.run()`` prepares your ``Manager`` instance to receive input from the command line.

The ``Manager`` class requires a single argument, the ``app_factory``. This is any function that returns
a ``Flask`` application instance. In the above example it is assumed that you have a ``create_app`` factory
function that returns a ready application.

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
--------------------------

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

Options must be created using the ``make_option`` function from the ``optparse <http://docs.python.org/library/optparse.html>``_ 
library.

API
---

.. module:: flaskext.script

.. _Flask: http://flask.pocoo.org
.. _Bitbucket: http://bitbucket.org/danjac/Flask-Script
