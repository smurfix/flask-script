Flask-Script
======================================

.. module:: Flask-Script

The **Flask-Script** extension provides support for writing external scripts in Flask. It uses `argparse`_ to parse command line arguments.

You define and add commands that can be called from the command line to a ``Manager`` instance::

    # manage.py
    
    from flaskext.script import Manager

    from myapp import app

    manager = Manager(app)
    
    @manager.command
    def hello(app):
        print "hello"

    if __name__ == "__main__":
        manager.run()

Then run the script like this::

    python manage.py hello
    > hello
    
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

The next step is to create and add your commands. There are three methods for creating commands:

    * subclassing the ``Command`` class
    * using the ``@command`` decorator
    * using the ``@option`` decorator

To take a very simple example, we want to create a ``Print`` command that just prints out "hello world". It 
doesn't take any arguments so is very straightforward::

    from flaskext.script import Command

    class Print(Command):

        description = "prints hello world"

        def run(self, app):
            print "hello world"

Now the command needs to be added to our ``Manager`` instance, created above::

    manager.add_command('print', Print())

This of course needs to be called before ``manager.run``. Now in our command line::

    python manage.py print
    > hello world

You can also pass the ``Command`` instance in a dict to ``manager.run()``::

    manager.run({'print' : Print()})

The first argument to your ``run`` command, other than ``self``, is always ``app``: this is the Flask
application instance provided by the ``app`` passed to the ``Manager``. Additional arguments
are configured through the ``option_list`` (see below).

To get a list of available commands and their descriptions, just run with no command::

    python manage.py

To get help text for a particular command::

    python manage.py runserver -h

This will print usage plus the docstring of the ``Command``.

The next method is using the ``@command`` decorator, which belongs to the ``Manager`` instance. 

This is probably the easiest to use, when you have a simple command::

    @manager.command
    def hello(app):
        "Just say hello"
        print "hello"

Commands created this way are run in exactly the same way as those created with the ``Command`` class::

    python manage.py hello
    > hello

As with the ``Command`` class, the docstring you use for the function will appear when you run with the **-h** option::

    python manage.py -h
    > Just say hello

Finally, the ``@option`` decorator, again belonging to ``Manager`` can be used when you want more sophisticated 
control over your commands::

    @manager.option('-n', '--name', help='Your name')
    def hello(app, name):
        print "hello", name

The ``@option`` command takes the exact same arguments as the ``Option`` instance - see the section on adding arguments
to commands below.

Note that with ``@command`` and ``@option`` decorators, the function must take the Flask application instance as the first
argument, just as with ``Command.run``.

Adding arguments to commands
----------------------------

Most commands take a number of named or positional arguments that you pass in the command line.

Taking the above examples, rather than just print "hello world" we would like to be able to print some
arbitrary name, like this::

    python manage.py hello --name=Joe
    hello Joe

or alternatively::

    python manage.py hello -n Joe

To facilitate this you use the ``option_list`` attribute of the ``Command`` class::

    from flaskext.script import Command, Manager, Option

    class Hello(Command):

        option_list = (
            Option('--name', '-n', dest='name'),
        )

        def run(self, app, name):
            print "hello %s" % name

Positional and optional arguments are stored as ``Option`` instances - see the API below for details.

Alternatively, you can define a ``get_options`` method for your ``Command`` class. This is useful if you want to be able
to return options at runtime based on for example per-instance attributes::

    class Hello(Command):

        def __init__(self, default_name='Joe'):
            self.default_name=default_name

        def get_options(self):
            return [
                Option('-n', '--name', dest='name', default=self.default_name),
            ]

        def run(self, app, name):
            print "hello",  name

If you are using the ``@command`` decorator, it's much easier - the options are extracted automatically from your function arguments::

    @manager.command
    def hello(app, name):
        print "hello", name


Then do::

    > python manage.py hello Joe
    hello joe

Or you can do optional arguments::

    @manager.command
    def hello(app, name="Fred")
        print hello, name

These can be called like this::

    > python manage.py hello --name=Joe
    hello Joe

alternatively::
    
    > python manage.py hello -n Joe
    hello Joe


and if you don't pass in any argument::

    > python manage.py hello 
    hello Fred

There are a couple of important points to note here.

The short-form **-n** is formed from the first letter of the argument, so "name" > "-n". Therefore it's a good idea that your
optional argument variable names begin with different letters ("app" is ignored, so don't worry about "a" being taken).

The second issue is that the **-h** switch always runs the help text for that command, so avoid arguments starting with the letter "h".

Note also that if your optional argument is a boolean, for example::

    @manage.command
    def verify(app, verified=False):
        """
        Checks if verified
        """
        print "VERIFIED?", "YES" if verified else "NO"

You can just call it like this::

    > python manage.py verify
    VERIFIED? NO

    > python manage.py verify -v
    VERIFIED? YES

    > python manage.py verify --verified
    VERIFIED? YES

For more complex options it's better to use the ``@option`` decorator::

    @manager.option('-n', '--name', dest='name', default='joe')
    def hello(app, name):
        print "hello", name

You can add as many options as you want::

    @manager.option('-n', '--name', dest='name', default='joe')
    @manager.option('-u', '--url', dest='url', default=None)
    def hello(app, name, url):
        if url is None:
            print "hello", name
        else:
            print "hello", name, "from", url

This can be called like so::

    > python manage.py hello -n Joe -u reddit.com
    hello Joe from reddit.com

or like this::
    
    > python manage.py hello --name=Joe --url=reddit.com
    hello Joe from reddit.com

Adding options to the manager
-----------------------------

Options can also be passed to the ``Manager`` instance. This is allows you to set up options that are passed to the application rather
than a single command. For example, you might want to have a flag to set the configuration file for your application::

    def create_app(config=None):
        
        app = Flask(__name__)
        if config is not None:
            app.config.from_pyfile(config)
        # configure your app...
        return app

In order to pass that ``config`` argument, use the ``add_option()`` method of your ``Manager`` instance. It takes the same arguments
as ``Option``::

    manager.add_option('-c', '--config', dest='config', required=False)

Suppose you have this command::
    
    @manager.command
    def hello(app, name):
        uppercase = app.config.get('USE_UPPERCASE', False)
        if uppercase:
            name = name.upper()
        print hello, name

You can now run the following::

    > python manage.py hello joe -c dev.cfg
    hello JOE

Assuming the ``USE_UPPERCASE`` setting is **True** in your dev.cfg file.

Notice also that the "config" option is **not** passed to the command.

In order for manager options to work it is assumed that you are passing a factory function, rather than a Flask instance, to your 
``Manager`` constructor.

Getting user input
------------------

**Flask-Script** comes with a set of helper functions for grabbing user input from the command line. For example::
    
    from flaskext.script import Manager, prompt_bool
    
    from myapp import app
    from myapp.models import db

    manager = Manager(app)
        
    @manager.command
    def dropdb(app):
        if prompt_bool(
            "Are you sure you want to lose all your data"):
            db.drop_all()

It then runs like this::

    python manage.py dropdb
    > Are you sure you want to lose all your data ? [N]

Default commands
----------------

**Flask-Script** has a couple of ready commands you can add and customize: ``Server`` and ``Shell``.

The ``Server`` command runs the **Flask** development server. It takes an optional ``port`` argument (default **5000**)::

    from flaskext.script import Server, Manager
    from myapp import create_app

    manager = Manager(create_app)
    manager.add_command("runserver", Server())

    if __name__ == "__main__":
        manager.run()

and then run the command::

    python manage.py runserver

The ``Server`` command has a number of command-line arguments - run ``python manage.py runserver -h`` for details on these.

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

The default commands **shell** and **runserver** are included by default, with the default options for these commands. If you wish to 
replace them with different commands simply override with ``add_command()`` or the decorators. If you pass ``with_default_commands=False``
to the ``Manager`` constructor these commands will not be loaded::

    manager = Manager(app, with_default_commands=False)


Accessing local proxies
-----------------------

The ``Manager`` runs the command inside a `Flask test context <http://flask.pocoo.org/docs/testing/#other-testing-tricks>`_. This means thathat you can access request-local proxies where appropriate, such as ``current_app``, which may be used by extensions.

API
---

.. module:: flaskext.script

.. autoclass:: Manager
   :members:
    
.. autoclass:: Command
   :members:

.. autoclass:: Shell

.. autoclass:: Server

.. class:: Option

    Stores option parameters for `argparse.ArgumentParser.add_argument <http://pypi.python.org/pypi/argparse>`_. Use with ``Command.option_list`` or ``Command.get_options()``. 

    .. method:: __init__(name_or_flags, action, nargs, const, default, type, choices, required, help, metavar, dest)

        :param name_or_flags: Either a name or a list of option strings, e.g. foo or -f, --foo
        :param action: The basic type of action to be taken when this argument is encountered at the command-line.
        :param nargs: The number of command-line arguments that should be consumed.
        :param const: A constant value required by some action and nargs selections.
        :param default: The value produced if the argument is absent from the command-line.
        :param type: The type to which the command-line arg should be converted.
        :param choices: A container of the allowable values for the argument.
        :param required: Whether or not the command-line option may be omitted (optionals only).
        :param help: A brief description of what the argument does.
        :param metavar: A name for the argument in usage messages.
        :param dest: The name of the attribute to be added to the object returned by parse_args().

.. autofunction:: prompt

.. autofunction:: prompt_bool

.. autofunction:: prompt_pass

.. autofunction:: prompt_choices

.. _Flask: http://flask.pocoo.org
.. _Bitbucket: http://bitbucket.org/danjac/flask-script
.. _argparse: http://pypi.python.org/pypi/argparse
