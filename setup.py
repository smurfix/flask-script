"""
Flask-Script
--------------

Flask support for writing external scripts.

Links
`````

* `documentation <http://packages.python.org/Flask-Script>`_
* `development version
  <http://bitbucket.org/danjac/flask-Script/get/tip.gz#egg=Flask-Script-dev>`_


"""
from setuptools import setup


setup(
    name='Flask-Script',
    version='0.3.1',
    url='http://bitbucket.org/danjac/flask-script',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    maintainer='Ron DuPlain',
    maintainer_email='ron.duplain@gmail.com',
    description='Scripting support for Flask',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'argparse',
    ],
    tests_require=[
        'nose',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
