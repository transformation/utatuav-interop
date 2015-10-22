Debugging & Team Evaluation
===========================

Server Log File
---------------

The competition server logs important events and debug information to a
temporary log file. The server writes useful debugging information to
``/var/log/apache2/auvsi_suas_server.debug.log``. Users can inspect this file
during or after competition server execution to debug interoperability. For
example, if your implementation is getting denied due to invalid user
credentials, the log will contain a message stating such and what request
parameters were provided at time of denial.

You can print out the file with the command:

.. code-block:: bash

    $ cat /var/log/apache2/auvsi_suas_server.debug.log

You can watch changes to the file live with the command:

.. code-block:: bash

    $ tail -f /var/log/apache2/auvsi_suas_server.debug.log

Evaluation Export CSV
---------------------

The competition server as a set of evaluation functions which can determine
information like which waypoints were hit by the UAS, how much time the UAS
spent out of bounds, what the min/max/average rate of interoperability was, and
what stationary and moving obstacles the UAS collided with. The admin interface
contains links to download this file per-mission.
