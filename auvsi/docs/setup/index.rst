System Setup
============

This section describes how to setup the system, whereas the next section
describes how to configure and use the system. Setup only needs to be
done once per deployment instance. Teams should do the following:

#. :doc:`downloading`.
   Use Git to download (clone) the repository and obtain the AUVSI SUAS
   competition system.
#. Automated System Setup. Automatically setup the system with :doc:`vagrant`,
   and for a :doc:`machine_or_vm` . This uses scripts to download, install, and
   execute Puppet with custom Puppet configuration scripts. This will install
   all system dependencies and setup the server.
#. :doc:`testing`.
   Test the setup by executing code correctness and max-load tests. You
   should ensure these tests pass before continuing to use the system.
#. :doc:`deployment`.
   The judges will follow steps to deploy the server for the
   competition. This will include enabling the Apache web server,
   disabling debug mode, and changing security secret keys. Teams do not
   need to do this for testing, but it will be done for the competition
   deployment.

--------------

.. toctree::
   :hidden:

   downloading
   vagrant
   machine_or_vm
   testing
   deployment
