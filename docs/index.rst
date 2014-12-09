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

    git clone https://github.com/smurfix/flask-script.git
    cd flask-script
    python setup.py develop

If you are using **virtualenv**, it is assumed that you are installing **Flask-Script**
in the same virtualenv as your Flask application(s).

Creating and running commands
-----------------------------

The first step is to create a Python module to run your script commands in. You can call it
anything you like, for our examples we'll call it ``manage.py``.

You don't have to place all your commands in the same file; for example, in a larger project
with lots of commands you might want to split them into a number of files with related commands.

In your ``manage.py`` file you have to create a ``Manager`` instance. The ``Manager`` class
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

To take a very simple example, we want to create a ``hello`` command that just prints out "hello world". It
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

    python manage.py runserver -?

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

As with the ``Command`` class, the docstring you use for the function will appear when you run with the ``-?`` or ``--help`` option::

    python manage.py -?
    > Just say hello

Finally, the ``@option`` decorator, again belonging to ``Manager`` can be used when you want more sophisticated
control over your commands::

    @manager.option('-n', '--name', help='Your name')
    def hello(name):
        print "hello", name

The ``@option`` decorator is explained in more detail below.

*New in version 2.0*

Help was previously available with ``--help`` and ``-h``. This had a couple
of less-than-ideal consequences, among them the inability to use ``-h`` as
a shortcut for ``--host`` or similar options.

*New in version 2.0.2*

If you want to restore the original meaning of ``-h``, set your manager's
``help_args`` attribute to a list of argument strings you want to be
considered helpful.

    manager = Manager()
    manager.help_args = ('-h','-?','--help)

You can override this list in sub-commands and -managers::

    def talker(host='localhost'):
        pass
    ccmd = ConnectCmd(talker)
    ccmd.help_args = ('-?','--help)
    manager.add_command("connect", ccmd)
    manager.run()

so that ``manager -h`` prints help, while ``manager connect -h fubar.example.com``
connects to a remote host.

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
        print "hello", name

These can be called like so::

    > python manage.py hello --name=Joe
    hello Joe

alternatively::

    > python manage.py hello -n Joe
    hello Joe

The short form ``-n`` is formed from the first letter of the argument, so "name" > "-n". Therefore it's a good idea for your
optional argument variable names to begin with different letters.

*New in version 2.0*

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
        print "hello", name

You can now run the following::

    > python manage.py -c dev.cfg hello joe
    hello JOE

Assuming the ``USE_UPPERCASE`` setting is **True** in your dev.cfg file.

Notice also that the "config" option is **not** passed to the command. In
fact, this usage

    > python manage.py hello joe -c dev.cfg

will show an error message because the ``-c`` option does not belong to the
``hello`` command.

You can attach same-named options to different levels; this allows you to
add an option to your app setup code without checking whether it conflicts with
a command:

    @manager.option('-n', '--name', dest='name', default='joe')
    @manager.option('-c', '--clue', dest='clue', default='clue')
    def hello(name,clue):
        uppercase = app.config.get('USE_UPPERCASE', False)
        if uppercase:
            name = name.upper()
            clue = clue.upper()
        print "hello {0}, get a {1}!".format(name,clue)

    > python manage.py -c dev.cfg hello -c cookie -n frank
    hello FRANK, get a COOKIE!

Note that the destination variables (command arguments, corresponding to
``dest`` values) must still be different; this is a limitation of Python's
argument parser.

In order for manager options to work you must pass a factory function, rather than a Flask instance, to your
``Manager`` constructor. A simple but complete example is available in `this gist <https://gist.github.com/smurfix/9307618>`_.

*New in version 2.0*

Before version 2, options and command names could be interspersed freely.
The author decided to discontinue this practice for a number of reasons;
the problem with the most impact was that it was not possible to do

    > python manage.py connect -d DEST
    > python manage.py import -d DIR

as these options collided.

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

    > python manage.py dropdb
    Are you sure you want to lose all your data ? [N]

See the :ref:`api` below for details on the various prompt functions.

Default commands
----------------

runserver
+++++++++

**Flask-Script** has a couple of ready commands you can add and customise: ``Server`` and ``Shell``.

The ``Server`` command runs the **Flask** development server.::

    from flask.ext.script import Server, Manager
    from myapp import create_app

    manager = Manager(create_app)
    manager.add_command("runserver", Server())

    if __name__ == "__main__":
        manager.run()

and then run the command::

    python manage.py runserver

The ``Server`` command has a number of command-line arguments - run ``python manage.py runserver -?`` for details on these. You can redefine the defaults in the constructor::

    server = Server(host="0.0.0.0", port=9000)

Needless to say the development server is not intended for production use.

*New in version 2.0.5*

The most common use-case for ``runserver`` is to run a debug server for
investigating problems. Therefore the default, if it is *not* set in the
configuration file, is to enable debugging and auto-reloading.

Unfortunately, Flask currently (as of May 2014) defaults to set the DEBUG
configuration parameter to ``False``. Until this is changed, you can
safely add ``DEFAULT=None`` to your Flask configuration. Flask-Script's
``runserver`` will then turn on debugging, but everything else will treat
it as being turned off.

To prevent misunderstandings -- after all, debug mode is a serious security
hole --, a warning is printed when Flask-Script treats a ``None`` default
value as if it were set to ``True``. You can turn on debugging explicitly
to get rid of this warning.

shell
+++++

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

This enables a ``shell`` command with the defaults enabled::

    > python manage.py shell

The default commands ``shell`` and ``runserver`` are included by default, with the default options for these commands. If you wish to
replace them with different commands simply override with ``add_command()`` or the decorators. If you pass ``with_default_commands=False``
to the ``Manager`` constructor these commands will not be loaded::

    manager = Manager(app, with_default_commands=False)

Sub-Managers
------------
A Sub-Manager is an instance of ``Manager`` added as a command to another Manager

To create a submanager::

    def sub_opts(app, **kwargs):
        pass
    sub_manager = Manager(sub_opts)

    manager = Manager(self.app)
    manager.add_command("sub_manager", sub_manager)

If you attach options to the sub_manager, the ``sub_opts`` procedure will
receive their values. Your application is passed in ``app`` for
convenience.

If ``sub_opts`` returns a value other than ``None``, this value will replace
the ``app`` value that's passed on. This way, you can implement a
sub-manager which replaces the whole app. One use case is to create a
separate administrative application for improved security::

    def gen_admin(app, **kwargs):
        from myweb.admin import MyAdminApp
        ## easiest but possibly incomplete way to copy your settings
        return MyAdminApp(config=app.config, **kwargs)
    sub_manager = Manager(gen_admin)

    manager = Manager(MyApp)
    manager.add_command("admin", sub_manager)

    > python manage.py runserver
    [ starts your normal server ]
    > python manage.py admin runserver
    [ starts an administrative server ]

You can cascade sub-managers, i.e. add one sub-manager to another. 

A sub-manager does not get default commands added to itself (by default)

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

Error handling
--------------

Users do not like to see stack traces, but developers want them for bug reports.

Therefore, ``flask.ext.script.command`` provides an `InvalidCommand` error
class which is not supposed to print a stack trace when reported.

In your command handler:

	from flask.ext.script.commands import InvalidCommand

    [… if some command verification fails …]
    class MyCommand(Command):
        def run(self, foo=None,bar=None):
            if foo and bar:
	            raise InvalidCommand("Options foo and bar are incompatible")

In your main loop:

    try:
        MyManager().run()
    except InvalidCommand as err:
        print(err, file=sys.stderr)
        sys.exit(1)

This way, you maintain interoperability if some plug-in code supplies
Flask-Script hooks you'd like to use, or vice versa.

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
.. _GitHub: http://github.com/smurfix/flask-script
