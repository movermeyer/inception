==============  ===============  =========  ============
VERSION         DOWNLOADS        TESTS      COVERAGE
==============  ===============  =========  ============
|pip version|   |pip downloads|  |travis|   |coveralls|
==============  ===============  =========  ============

**STILL UNDER HEAVY DEVELOPMENT**

Checkout the repository_.

Goal and Philosophy
===================

Manages templates to allow projects inception.

I'm tired of doing repetitive steps whenever I create a new project: configure Travis, add the ``.gitignore``, create a new ``setup.py``, etc. So I decided to automate it. And I want anybody can contribute with templates **without any Python knowledge**.

This project is in its first stages, so do not be too tidy.


How to use it
=============

Installation
------------

From pypi:

.. code::

   pip install inception

From the main repository:

.. code::

   git clone https://github.com/magmax/inception.git


Usage
-----

As easy as:

.. code::

   python inception/__main__.py --template-path TEMPLATE -o OUTPUT_PATH


Template creation
=================

The idea is to maintain easy but powerful templates. Learning Python is not required, but useful.

To create a new template, there is just one requirement: the settings.py file.


settings.py file
----------------

This file contains the settings to rule the inception. It will contains some variables (just Python_ vars).

The main one is ``program``, that is a vector. here you have an example:

.. code::

    # as vector
    program = [
        inquire(),
        copy(),
    ]



Any operation inside the ``program`` vector is a "promise". This means it won't be evaluated until it is called later.

There are several preloaded promises, but you can write your own. We will come back to this later.

``inquire`` promise
~~~~~~~~~~~~~~~~~~~

Requires information from the user.

As parameter, you can pass an array of Questions, as it is defined in inquirer_. If no argument is supplied, it will try to get the ``QUESTIONS`` variable from the settings file.

Next examples are equivalent:

.. code::

    QUESTIONS = [
        { "kind": "text",
          "name": "name",
          "message": "What's your name"
        },
    ]

    program = [
        inquire(),
    ]

.. code::

    QUESTIONS = [
        { "kind": "text",
          "name": "name",
          "message": "What's your name"
        },
    ]

    program = [
        inquire(QUESTIONS),
    ]

.. code::

    program = [
        inquire([
            { "kind": "text",
              "name": "name",
              "message": "What's your name"
            },
        ]),
    ]

``copy`` promise
~~~~~~~~~~~~~~~~

This promise will copy some directory structure from our templates to the output directory. The directory structure will be copied **as is**, this means you will have to repeat the whole tree you want to build.

It allows an argument, that is the directory to be used as source. If no argument is supplied, ``files`` will be used.

If any file ends with ``.jinja``, it will be managed as a jinja_ template, replacing any variable inside with any variable taken with the ``inquire`` promise.

This structure is valid for file names too.

Structures examples:

.. code::

    .
    ├── files
    │   └── level_1
    │       └── level_2
    │           ├── example1.txt
    │           ├── example2.txt.jinja
    │           └── {{ name }}.txt
    └── settings.py

with  ``name="example3"`` will produce:

.. code::

    output
    └── level_1
        └── level_2
            ├── example1.txt
            ├── example2.txt
            └── example3.txt

Existing files won't be overriden.


``run`` promise
~~~~~~~~~~~~~~~

Executes any command line script. The script should be provided as first argument. Example:

.. code::

   program = [
       run('virtualenv venv'),
   ]

Pipes are not allowed.


Creating your own promises
--------------------------

Python knowledge is required to do this.

They can be defined inside the ``settings.py`` module or to be imported from other modules in the ``settings.py``

A promise is just a function returning another function. Inner function should match the pattern:

.. code:: python

          def inner(config, template_path, output):
              pass

There are two ways to do this: with functions or classes.

Function promises
~~~~~~~~~~~~~~~~~

An example is better than a thausand words:

.. code:: python

    def my_promise(argument_1, argument_2):
        def inner(config, template_path, output):
            # do whatever with argument_1, argument_2, and the others
            pass
        return inner

Class promises
~~~~~~~~~~~~~~

Same example:

.. code:: python

    class my_promise(object):
        def __init__(self, argument_1, argument_2):
            self._arg1 = argument_1
            self._arg2 = argument_2

        def __call__(self, config, template_path, output):
            # do whatever with argument_1, argument_2, and the others
            pass

Promises usage
~~~~~~~~~~~~~~

Both class and function promises are used in the same way:

.. code:: python

          program = [
              my_promise('argument_1', 'argument_2')
          ]



To do list
==========

Things I'd like to add to inception:

- a Downloader class, that retrieves the package from github.
- a file with the list of available templates, to use its name instead its directory. This will allow to improve the Downloader class.
- better output
- tests.
- debianize it.


License
=======

Copyright (c) 2014 Miguel Ángel García (`@magmax9`_).

Licensed under `the MIT license`_.


.. |travis| image:: https://travis-ci.org/magmax/inception.png
  :target: `Travis`_
  :alt: Travis results

.. |coveralls| image:: https://coveralls.io/repos/magmax/inception/badge.png
  :target: `Coveralls`_
  :alt: Coveralls results_

.. |pip version| image:: https://pypip.in/v/inception/badge.png
    :target: https://pypi.python.org/pypi/inception
    :alt: Latest PyPI version

.. |pip downloads| image:: https://pypip.in/d/inception/badge.png
    :target: https://pypi.python.org/pypi/inception
    :alt: Number of PyPI downloads

.. _Travis: https://travis-ci.org/magmax/inception
.. _Coveralls: https://coveralls.io/r/magmax/inception

.. _@magmax9: https://twitter.com/magmax9

.. _the MIT license: http://opensource.org/licenses/MIT
.. _download the lastest zip: https://pypi.python.org/pypi/inception
.. _inquirer: https://travis-ci.org/magmax/python-inquirer
.. _repository: https://travis-ci.org/magmax/inception
.. _jinja: http://jinja.pocoo.org/
