Interoperability Example
========================

The following is an example of how to perform interoperability using the
``curl`` command. **This is too inefficient to achieve a sufficient
update rate**. This merely shows how simple it is to implement
interoperability.

The curl command has the following parameters:

#. **-b**: The place to save received cookies.
#. **-c**: The place to load and send cookies.
#. **--data**: Makes the request a POST request instead of GET request,
   and sends the given argument as the POST data segment.
#. **[URL]**: The URL to make a request to. This consists of a hostname
   (localhost:8080) and a relative path (/api/interop/server\_info).

Try the following commands, and see the effect on the stored data at the
server:

.. code-block:: bash

    $ curl -b cookies.txt -c cookies.txt \
         --data "username=testuser&password=testpass" \
         http://localhost:8080/api/login

    $ curl -b cookies.txt -c cookies.txt \
         http://localhost:8080/api/server_info

    $ curl -b cookies.txt -c cookies.txt \
         http://localhost:8080/api/obstacles

    $ curl -b cookies.txt -c cookies.txt \
         --data "latitude=10&longitude=20&altitude_msl=30&uas_heading=40" \
         http://localhost:8080/api/telemetry
