from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'multipass',
    version          = '1.2.8',
    description      = 'An app to make multiple passes or runs of a certain Python Utility with different args',
    long_description = readme,
    author           = 'FNNDSC/ArushiVyas',
    author_email     = 'dev@babyMRI.org',
    url              = 'https://github.com/FNNDSC/pl-multipass',
    packages         = ['multipass'],
    install_requires = ['chrisapp'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.8',
    entry_points     = {
        'console_scripts': [
            'multipass = multipass.__main__:main'
            ]
        }
)
