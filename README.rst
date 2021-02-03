pl-multipass
================================

.. image:: https://travis-ci.org/FNNDSC/multipass.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/multipass

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
    :target: https://github.com/FNNDSC/pl-multipass/blob/master/setup.py

.. contents:: Table of Contents


Abstract
--------

Simply execute the same target application multiple times over the same input space, with each execution tuned to a different set of CLI flags/values.


Description
-----------

``multipass`` is a very simple script that runs a specific ``<appToRun>`` on the underlying system shell multiple times over the same ``<inputDir>``. Each run, or pass, differs in the set of ``<pipeSeparatedSpecificArgs>`` that is passed to the app.

In each pass, the ``<commonArgs>`` remains constant.

The main purpose of this plugin is to allow for one simple mechanism of running slightly different flags over the same ``<inputDir>`` space in several phases, and capturing the multiple outputs in the ``<outputDir>``. In the context of a ``ChRIS`` feed tree, this has the effect of having one feed thread contain effectively multiple runs of some ``<appToRun>`` in one ``<outputDir>``. In some cases this can be a useful execution model.


Usage
-----

.. code::

    multipass
            [--exec <appToRun>]                                         \
            [--specificArgs <pipeSeparatedSpecificArgs>]                \
            [--commonArgs <commonArgs>]                                 \
            [-h] [--help]                                               \
            [--json]                                                    \
            [--man]                                                     \
            [--meta]                                                    \
            [--savejson <DIR>]                                          \
            [--noJobLogging]                                            \
            [-v <level>] [--verbosity <level>]                          \
            [--version]                                                 \
            <inputDir>                                                  \
            <outputDir>


Arguments
~~~~~~~~~

.. code::

        [--exec <appToRun>]
        A specific ``app`` to run in _multi-phase_ mode. This app must by
        necessity exist within the  ``multiphase`` container. See the
        ``requirements.txt`` for list of installed apps

        [--specificArgs <pipeSeparatedSpecificArgs>]
        This is a string list of per-phase specific arguments. Each
        phase is separeted by the pipe ``|`` character.

        [--commonArgs <commonArgs>]
        This is a raw string of args, common to each phase call of the
        <appToRun>.

        [-h] [--help]
        If specified, show help message and exit.

        [--json]
        If specified, show json representation of app and exit.

        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.

        [--savejson <DIR>]
        If specified, save json representation file to DIR and exit.

        [--noJobLogging]
        Turns off per-job logging to file system.

        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.

        [--version]
        If specified, print version number and exit.


Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-multipass multipass --man

Run
~~~

You need you need to specify input and output directories using the `-v` flag to `docker run`.


.. code:: bash

    docker run --rm -u $(id -u)                                     \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing              \
        fnndsc/pl-multipass multipass                               \
        /incoming /outgoing


Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-multipass .

Examples
--------

Put some examples here!


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
