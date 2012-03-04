"""
Flask-Script
--------------

Flask support for writing external scripts.

Links
`````

* `documentation <http://packages.python.org/Flask-Script>`_


"""
from setuptools import setup


setup(
    name='Flask-Script',
    version='0.3.2',
    url='http://github.com/rduplain/flask-script',
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
