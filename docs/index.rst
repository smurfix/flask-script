Flask-Script
======================================

.. module:: Flask-Script

The **Flask-Script** extension provides support for writing external scripts in Flask. This includes running a development server, a customised Python shell, scripts to set up your database, cronjobs, and other command-line tasks that belong outside the web application itself.

**Flask-Script** works in a similar way to Flask itself. You define and add commands that can be called from the command line to a ``Manager`` instance::

    # manage.py

    from flask.ext.script import Manager

    from myapp import app

    manager = Manager(app)

    @manager.command
    def hello():
        print "hello"

    if __name__ == "__main__":
        manager.run()

Once you define your script commands, you can then run them on the command line::

    python manage.py hello
    > hello

Source code and issue tracking at `GitHub`_.

Installing Flask-Script
------------------------

Install with **pip** and **easy_install**::

    pip install Flask-Script

or download the latest version from version control::

    git clone https://github.com/techniq/flask-script.git
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

    from flask.ext.script import Manager

    app = Flask(__name__)
    # configure your app

    manager = Manager(app)

    if __name__ == "__main__":
        manager.run()

Calling ``manager.run()`` prepares your ``Manager`` instance to receive input from the command line.

The ``Manager`` requires a single argument, a **Flask** instance. This may also be a function or other callable
that returns a **Flask** instance instead, if you want to use a factory pattern.

The next step is to create and add your commands. There are three methods for creating commands:

    * subclassing the ``Command`` class
    * using the ``@command`` decorator
    * using the ``@option`` decorator

To take a very simple example, we want to create a **Hello** command that just prints out "hello world". It
doesn't take any arguments so is very straightforward::

    from flask.ext.script import Command

    class Hello(Command):
        "prints hello world"

        def run(self):
            print "hello world"

Now the command needs to be added to our ``Manager`` instance, like the one created above::

    manager.add_command('hello', Hello())

This of course needs to be called before ``manager.run``. Now in our command line::

    python manage.py hello
    > hello world

You can also pass the ``Command`` instance in a dict to ``manager.run()``::

    manager.run({'hello' : Hello()})

The ``Command`` class must define a ``run`` method. The positional and optional arguments
depend on the command-line arguments you pass to the ``Command`` (see below).

To get a list of available commands and their descriptions, just run with no command::

    python manage.py

To get help text for a particular command::

    python manage.py runserver -h

This will print usage plus the docstring of the ``Command``.

This first method is probably the most flexible, but it's also the most verbose. For simpler commands you can use
the ``@command`` decorator, which belongs to the ``Manager`` instance::

    @manager.command
    def hello():
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
    def hello(name):
        print "hello", name

The ``@option`` decorator is explained in more detail below.


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

    from flask.ext.script import Command, Manager, Option

    class Hello(Command):

        option_list = (
            Option('--name', '-n', dest='name'),
        )

        def run(self, name):
            print "hello %s" % name

Positional and optional arguments are stored as ``Option`` instances - see the :ref:`api` below for details.

Alternatively, you can define a ``get_options`` method for your ``Command`` class. This is useful if you want to be able
to return options at runtime based on for example per-instance attributes::

    class Hello(Command):

        def __init__(self, default_name='Joe'):
            self.default_name=default_name

        def get_options(self):
            return [
                Option('-n', '--name', dest='name', default=self.default_name),
            ]

        def run(self, name):
            print "hello",  name

If you are using the ``@command`` decorator, it's much easier - the options are extracted automatically from your function arguments. This is an example of a positional argument::

    @manager.command
    def hello(name):
        print "hello", name

You then invoke this on the command line like so::

    > python manage.py hello Joe
    hello Joe

Or you can do optional arguments::

    @manager.command
    def hello(name="Fred")
        print hello, name

These can be called like so::

    > python manage.py hello --name=Joe
    hello Joe

alternatively::

    > python manage.py hello -n Joe
    hello Joe

There are a couple of important points to note here.

The short-form **-n** is formed from the first letter of the argument, so "name" > "-n". Therefore it's a good idea that your
optional argument variable names begin with different letters.

The second issue is that the **-h** switch always runs the help text for that command, so avoid arguments starting with the letter "h".

Note also that if your optional argument is a boolean, for example::

    @manage.command
    def verify(verified=False):
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

The ``@command`` decorator is fine for simple operations, but often you need the flexibility. For more sophisticated options it's better to use the ``@option`` decorator::

    @manager.option('-n', '--name', dest='name', default='joe')
    def hello(name):
        print "hello", name

You can add as many options as you want::

    @manager.option('-n', '--name', dest='name', default='joe')
    @manager.option('-u', '--url', dest='url', default=None)
    def hello(name, url):
        if url is None:
            print "hello", name
        else:
            print "hello", name, "from", url

This can be called like so::

    > python manage.py hello -n Joe -u reddit.com
    hello Joe from reddit.com

or alternatively::

    > python manage.py hello --name=Joe --url=reddit.com
    hello Joe from reddit.com

Adding options to the manager
-----------------------------

Options can also be passed to the ``Manager`` instance. This is allows you to set up options that are passed to the application rather
than a single command. For example, you might want to have a flag to set the configuration file for your application. Suppose you create
your application with a factory function::

    def create_app(config=None):

        app = Flask(__name__)
        if config is not None:
            app.config.from_pyfile(config)
        # configure your app...
        return app

You want to be able to define the ``config`` argument on the command line - for example, if you have a command to set up your database, you
most certainly want to use different configuration files for production and development.

In order to pass that ``config`` argument, use the ``add_option()`` method of your ``Manager`` instance. It takes the same arguments
as ``Option``::

    manager.add_option('-c', '--config', dest='config', required=False)

As with any other **Flask-Script** configuration you can call this anywhere in your script module, but it must be called before your ``manager.run()`` call.

Suppose you have this command::

    @manager.command
    def hello(name):
        uppercase = app.config.get('USE_UPPERCASE', False)
        if uppercase:
            name = name.upper()
        print hello, name

You can now run the following::

    > python manage.py hello joe -c dev.cfg
    hello JOE

Assuming the ``USE_UPPERCASE`` setting is **True** in your dev.cfg file.

Notice also that the "config" option is **not** passed to the command.

In order for manager options to work you must pass a factory function, rather than a Flask instance, to your
``Manager`` constructor. A simple but complete example is available in `this gist <https://gist.github.com/3531881>`_.

Getting user input
------------------

**Flask-Script** comes with a set of helper functions for grabbing user input from the command line. For example::

    from flask.ext.script import Manager, prompt_bool

    from myapp import app
    from myapp.models import db

    manager = Manager(app)

    @manager.command
    def dropdb():
        if prompt_bool(
            "Are you sure you want to lose all your data"):
            db.drop_all()

It then runs like this::

    python manage.py dropdb
    > Are you sure you want to lose all your data ? [N]

See the :ref:`api` below for details on the various prompt functions.

Default commands
----------------

**Flask-Script** has a couple of ready commands you can add and customise: ``Server`` and ``Shell``.

The ``Server`` command runs the **Flask** development server. It takes an optional ``port`` argument (default **5000**)::

    from flask.ext.script import Server, Manager
    from myapp import create_app

    manager = Manager(create_app)
    manager.add_command("runserver", Server())

    if __name__ == "__main__":
        manager.run()

and then run the command::

    python manage.py runserver

The ``Server`` command has a number of command-line arguments - run ``python manage.py runserver -h`` for details on these. You can redefine the defaults in the constructor::

    server = Server(host="0.0.0.0", port=9000)

Needless to say the development server is not intended for production use.

The ``Shell`` command starts a Python shell. You can pass in a ``make_context`` argument, which must be a ``callable`` returning a ``dict``. By default, this is just a dict returning the your Flask application instance::

    from flask.ext.script import Shell, Manager

    from myapp import app
    from myapp import models
    from myapp.models import db

    def _make_context():
        return dict(app=app, db=db, models=models)

    manager = Manager(create_app)
    manager.add_command("shell", Shell(make_context=_make_context))

This is handy if you want to include a bunch of defaults in your shell to save typing lots of ``import`` statements.

The ``Shell`` command will use `IPython <http://ipython.scipy.org/moin/>`_ if it is installed, otherwise it defaults to the standard Python shell. You can disable this behaviour in two ways: by passing the ``use_ipython`` argument to the ``Shell`` constructor, or passing the flag ``--no-ipython`` in the command line::

    shell = Shell(use_ipython=False)

There is also a ``shell`` decorator which you can use with a context function::

    @manager.shell
    def make_shell_context():
        return dict(app=app, db=db, models=models)

This enables a **shell** command with the defaults enabled::

    > python manage.py shell

The default commands **shell** and **runserver** are included by default, with the default options for these commands. If you wish to
replace them with different commands simply override with ``add_command()`` or the decorators. If you pass ``with_default_commands=False``
to the ``Manager`` constructor these commands will not be loaded::

    manager = Manager(app, with_default_commands=False)

Sub-Managers
------------
A Sub-Manager is an instance of ``Manager`` added as a command to another Manager

To create a submanager::

    sub_manager = Manager()

    manager = Manager(self.app)
    manager.add_command("sub_manager", sub_manager)

Restrictions
    - A sub-manager does not provide an app instance/factory when created, it defers the calls to it's parent Manager's
    - A sub-manager inhert's the parent Manager's app options (used for the app instance/factory)
    - A sub-manager does not get default commands added to itself (by default)
    - A sub-manager must be added the primary/root ``Manager`` instance via ``add_command(sub_manager)``
    - A sub-manager can be added to another sub-manager as long as the parent sub-manager is added to the primary/root Manager

*New in version 0.5.0.*

Note to extension developers
----------------------------
Extension developers can easily create convenient sub-manager instance within their extensions to make it easy for a user to consume all the available commands of an extension.

Here is an example how a database extension could provide (ex. database.py)::

    manager = Manager(usage="Perform database operations")

    @manager.command
    def drop():
        "Drops database tables"
        if prompt_bool("Are you sure you want to lose all your data"):
            db.drop_all()


    @manager.command
    def create(default_data=True, sample_data=False):
        "Creates database tables from sqlalchemy models"
        db.create_all()
        populate(default_data, sample_data)


    @manager.command
    def recreate(default_data=True, sample_data=False):
        "Recreates database tables (same as issuing 'drop' and then 'create')"
        drop()
        create(default_data, sample_data)


    @manager.command
    def populate(default_data=False, sample_data=False):
        "Populate database with default data"
        from fixtures import dbfixture

        if default_data:
            from fixtures.default_data import all
            default_data = dbfixture.data(*all)
            default_data.setup()

        if sample_data:
            from fixtures.sample_data import all
            sample_data = dbfixture.data(*all)
            sample_data.setup()


Then the user can register the sub-manager to their primary Manager (within manage.py)::

    manager = Manager(app)

    from flask.ext.database import manager as database_manager
    manager.add_command("database", database_manager)

The commands will then be available::

    > python manage.py database

     Please provide a command:

     Perform database operations
      create    Creates database tables from sqlalchemy models
      drop      Drops database tables
      populate  Populate database with default data
      recreate  Recreates database tables (same as issuing 'drop' and then 'create')

Accessing local proxies
-----------------------

The ``Manager`` runs the command inside a `Flask test context <http://flask.pocoo.org/docs/testing/#other-testing-tricks>`_. This means that you can access request-local proxies where appropriate, such as ``current_app``, which may be used by extensions.

.. _api:

API
---

.. module:: flask_script

.. autoclass:: Manager
   :members: run, add_option, add_command, command, option, shell, get_usage, print_usage

.. autoclass:: Command
   :members: run, get_options

.. autoclass:: Shell

.. autoclass:: Server

.. autoclass:: Option

.. autoclass:: Group

.. autofunction:: prompt

.. autofunction:: prompt_bool

.. autofunction:: prompt_pass

.. autofunction:: prompt_choices

.. _Flask: http://flask.pocoo.org
.. _GitHub: http://github.com/techniq/flask-script
.. _argparse: http://pypi.python.org/pypi/argparse
