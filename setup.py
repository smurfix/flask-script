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

# Hack to prevent stupid TypeError: 'NoneType' object is not callable error on
# exit of python setup.py test # in multiprocessing/util.py _exit_function when
# running python setup.py test (see
# https://github.com/pypa/virtualenv/pull/259)
try:
    import multiprocessing
except ImportError:
    pass

install_requires = ['Flask']
if sys.version_info < (2, 7):
    install_requires += ['argparse']

setup(
    name='Flask-Script',
    version='0.5.1',
    url='http://github.com/techniq/flask-script',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    maintainer='Sean Lynch',
    maintainer_email='techniq35@gmail.com',
    description='Scripting support for Flask',
    long_description=__doc__,
    py_modules=[
        'flask_script'
    ],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
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
