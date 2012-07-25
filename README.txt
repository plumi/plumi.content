.. contents::

Plumi Content Types package

- Code repository: https://github.com/plumi/plumi.content
- Questions and comments to discuss@lists.plumi.org
- Report bugs at http://plumi.org/newticket

Installation
------------
::

    python2.6 bootstrap.py
    ./bin/buildout


Usage
-----
Start zeo::

    ./bin/zeoserver start

Start the transcode daemon::

    ./bin/transcodedaemon start # or fg to start it in the foreground

Start the worker instance::

    ./bin/worker start

Start Zope::

    ./bin/instance start


Add a new Plone site, go to the Install Products Form and install Plumi content
and transcode.star.


