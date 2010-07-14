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

Accessing local proxies
-----------------------

The ``Manager`` runs the command inside a `Flask test context <http://flask.pocoo.org/docs/testing/#other-testing-tricks>`_. This means thathat you can access request-local proxies where appropriate, such as ``current_app``, which may be used by extensions.

API
---

.. module:: flaskext.script

.. class:: Manager
    
    Manages a set of commands.

    .. method:: __init__(app)

        :param app: **Flask** application instance or callable that returns a **Flask** application.

    .. method:: run(commands=None)

        Run a command based on command-line inputs. Typically you would call this inside a ``if __name__ == "__main__"`` block.

        :param commands: optional dict of ``Command`` instances.

    .. method:: command(func)

        Decorator to add a function as a command. The function must take at least one argument, the Flask instance. Additional 
        positional or optional arguments are added to the command line options.

    .. method:: option(func, `*args`, `**kwargs`)
        
        Decorator to add option to a function. Use this instead of ``command``. You can use this decorator multiple times to 
        add as many options as you need.
        
.. class:: Command

    Base class for creating new commands.

    .. attribute:: description

    Description added to help text.
    **This is deprecated:** use docstring instead. 

    .. attribute:: option_list

    List of options passed to argument parser. Each item must be an ``Option`` instance.

    .. method:: get_options()

    Returns list of ``Option`` instances. By default just returns ``option_list``. This is useful if you need to do per-instance configuration. 

    .. method:: run(app)

    Runs the command. This must be defined or ``NotImplementedError`` is raised. Takes at least one argument, ``app``, plus any specific positional or optional arguments required by the command.

    
    :param app: Flask application instance

    .. method:: prompt(prompt, default=None)

    Prompts the user for input, if ``default`` is provided then that is used instead.
    **This is deprecated** : use prompt() function instead.

    :param prompt: formatted prompt text
    :param default: default if no input entered

    .. method:: prompt_pass(prompt, default=None)

    Prompts the user for hidden (password) input, if ``default`` is provided then that is used instead.
    **This is deprecated** : use prompt_pass() function instead.

    :param prompt: formatted prompt text
    :param default: default if no input entered


    .. method:: prompt_choices(prompt, choices, default=None)

    Prompts the user for input from available choices, if ``default`` is provided then that is used instead.
    **This is deprecated** : use prompt_choices() function instead.

    :param prompt: formatted prompt text
    :param choices: list of available choices
    :param default: default if no input entered


    .. method:: prompt_bool(prompt, default=False)

    Prompts the user for input, if ``default`` is provided then that is used instead. A boolean value is 
    returned based on selection of input ('y', 'yes', 'n', 'no' etc).
    **This is deprecated** : use prompt_bool() function instead.

    :param prompt: formatted prompt text
    :param default: default if no input entered

.. class:: Shell

    Command to start a Python shell.

    .. method:: __init__(banner='', make_context=None)

        :param banner: banner appearing in shell when started.
        :param make_context: a function that must return a ``dict``. If you wish to add any context variables to your shell namespace, then add them here. The ``make_context`` function takes one argument, ``app``. By default the ``app`` instance is passed to the shell.

.. class:: Server

    Command to start the Flask development server.

    .. method:: __init__(host='127.0.0.1', port=5000, use_debugger=True, use_reloader=True)

        :param host: hostname. Can be overriden with **--host** command-line option.
        :param port: port. Can be overriden with **--port** command-line option.
        :param use_debugger: whether to use the Flask debugger. If ``False`` can be overriden by **--debug** command-line option.
        :param use_reloader: whether to use the Flask auto-reloader. If ``False`` can be overriden by **--reload** command-line option.

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

.. _Flask: http://flask.pocoo.org
.. _Bitbucket: http://bitbucket.org/danjac/flask-script
.. _argparse: http://pypi.python.org/pypi/argparse
