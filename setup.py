"""
Flack
-----
Flask extension for gathering feedback
"""
from flask_flack import __version__
from setuptools import setup
import sys

requires = ['Flask>=0.9']

setup(
    name='Flask-Flack',
    version=__version__,
    url='https://github.com/thrisp/flack.git',
    license='BSD',
    author='thrisp/hurrata',
    author_email='blueblank@gmail.com',
    description='feedback extension for flask',
    long_description=__doc__,
    packages=['flask_flack'],
    zip_safe=False,
    platforms='any',
    install_requires=requires,
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
