"""
Flask-Script
--------------

Flask support for writing external scripts.

Links
`````

* `documentation <http://flask-script.readthedocs.org>`_


"""
import sys
from setuptools import setup

version='2.0.6'

# Hack to prevent stupid TypeError: 'NoneType' object is not callable error on
# exit of python setup.py test # in multiprocessing/util.py _exit_function when
# running python setup.py test (see
# https://github.com/pypa/virtualenv/pull/259)
try:
    import multiprocessing
except ImportError:
    pass

install_requires = ['Flask']

setup(
    name='Flask-Script',
    version=version,
    url='http://github.com/smurfix/flask-script',
	download_url = 'https://github.com/smurfix/flask-script/tarball/v'+version,
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    maintainer='Matthias Urlichs',
    maintainer_email='matthias@urlichs.de',
    description='Scripting support for Flask',
    long_description=__doc__,
    packages=[
        'flask_script'
    ],
    zip_safe=False,
    install_requires=install_requires,
    tests_require=[
        'pytest',
    ],
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
