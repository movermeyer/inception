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

I'm tired of doing repetitive steps whenever I create a new project: configure Travis, add the ``.gitignore``, create a new ``setup.py``, etc. So I decided to automate it.

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

The idea is to maintain easy templates. So, there are two main stages:

#. Ask the user for some data
#. Generate the result.

Let's see how to configure these steps.

settings.py
-----------

This file should contain an uppercase variable called ``QUESTIONS``, containing a list of questions. It uses the inquirer_ format, and you can return a string.

Example:

.. code::

    QUESTIONS = [
        { "kind": "text",
          "name": "name",
          "message": "What's your name"
        },
        { "kind": "text",
          "name": "surname",
          "message": "What's your surname"
        },
        { "kind": "list",
          "name": "size",
          "message": "What size do you need?",
          "choices": ["Jumbo", "Large", "Standard", "Medium", "Small", "Micro"]
        }
    ]


files
-----

In order to generate the result, you have to store files in the ``files`` directory.

Any directory in the ``files`` directory will be created in the ``output`` directory.
Any file ending in ``.jinja`` will be managed as a jinja_ template, using the variables retrieved by the ``QUESTIONS``.
Any other file will be copied as it is.

Existing files won't be overriden. You have to remove them in order to regenerate them.

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
