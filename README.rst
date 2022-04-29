Pelican Static Comment System
=============================

Pelican Static Comment System allows you to add static comments to your
articles.

.. image:: https://img.shields.io/pypi/v/minchin.pelican.plugins.static-comments.svg?style=flat
    :target: https://pypi.python.org/pypi/minchin.pelican.plugins.static-comments/
    :alt: PyPI version number

.. image:: https://img.shields.io/badge/-Changelog-success
   :target: https://github.com/MinchinWeb/minchin.pelican.plugins.static-comments/blob/master/CHANGELOG.rst
   :alt: Changelog

.. image:: https://img.shields.io/pypi/pyversions/minchin.pelican.plugins.static-comments?style=flat
    :target: https://pypi.python.org/pypi/minchin.pelican.plugins.static-comments/
    :alt: Supported Python version

.. image:: https://img.shields.io/pypi/l/minchin.pelican.plugins.static-comments.svg?style=flat&color=green
    :target: https://github.com/MinchinWeb/minchin.pelican.plugins.static-comments/blob/master/LICENSE.txt
    :alt: License

.. image:: https://img.shields.io/pypi/dm/minchin.pelican.plugins.static-comments.svg?style=flat
    :target: https://pypi.python.org/pypi/minchin.pelican.plugins.static-comments/
    :alt: Download Count

Comments are received via email (i.e. you don't need to maintain a server to
receive comments). Comments are stored in files in formats that can be
processed by Pelican (e.g., Markdown, reStructuredText). Each comment resides
in its own file.

Features
--------

-  Static comments for each article
-  Replies to comments
-  Avatars and `Identicons <https://en.wikipedia.org/wiki/Identicon>`__
-  Comment Atom feed for each article
-  Easily style-able via themes
-  Python 3 support

See it in action here:
`bernhard.scheirle.de <http://bernhard.scheirle.de/posts/2014/March/29/static-comments-via-email/>`__

+-------------------+-----------------------------+-----------------------------------------------+
| Author            | Website                     | Github                                        |
+===================+=============================+===============================================+
| Bernhard Scheirle | http://bernhard.scheirle.de | https://github.com/Scheirle                   |
+-------------------+-----------------------------+-----------------------------------------------+
| William Minchin   | https://blog.minchin.ca     | https://github.com/MinchinWeb/blog.minchin.ca |
+-------------------+-----------------------------+-----------------------------------------------+

Instructions
------------

-  `Quickstart Guide <docs/quickstart.md>`__
-  `Installation and basic usage <docs/installation.md>`__
-  `Import existing comments <docs/import.md>`__
-  `Avatars and identicons <docs/avatars.md>`__
-  `Comment Atom feed <docs/feed.md>`__
-  `[Developer] How to do a release <docs/how-to-release.md>`__

PyPi
------------
The Pelican Comment System is now also in the Python Package Index and can
easily installed via:

::

    pip install minchin.pelican.plugins.static-comments


Requirements
------------

Pelican 3.4 or newer is required.

To create identicons, the Python Image Library is needed. Therefore you either
need PIL **or** Pillow (recommended). If you install the plugin from pip,
Pillow will automatically be installed.

**Install Pillow manually via:**

::

    pip install Pillow

If you don't want avatars or identicons, this plugin works fine without
PIL/Pillow. You will, however, see a warning that identicons are deactivated
(as expected).

Change Log
----------

The change log can be found in the `CHANGELOG.rst <./CHANGELOG.rst>`__
file.
