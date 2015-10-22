Machine or VirtualBox Setup
===========================

You need either a dedicated machine or a virtual machine (VM) to run the
competition server. Using a dedicated machine or VirtualBox will require
manual setup, which is described in this section. Either method will
require at least 13 GB of disk space. It is recommended to reserve at
least 20 GB.

Create Dedicated Machine
------------------------

#. **Install the Operating System (OS)**. Install :doc:`/prerequisites/ubuntu`
   onto the machine. Create a user with administration privileges (e.g.
   the one creates at OS install) and login as that user.

Create Machine using VirtualBox
-------------------------------

#. **Create a Virtual Machine**.
   :doc:`/prerequisites/virtualbox` can be used to manage a virtual machine.
   You will need to create a disk with at least 13GB of space.
#. **Install the Operating System (OS)**. Install :doc:`/prerequisites/ubuntu`
   onto the machine. Create a user with administration privileges (e.g.
   the one creates at OS install) and login as that user.

Setup Machine using Vagrant
---------------------------

#. **Download the Repository**. To setup a virtual machine using Vagrant
   you will need the Vagrantfile, a file which defines the machine
   configuration. You will need to first download the repository onto
   the host machine, for which instructions can be found
   :doc:`here <downloading>`.
#. **Install Vagrant**. You will then need to install
   `Vagrant <https://www.vagrantup.com/>`__. Please follow the
   instructions for downloading and installing on your host machine, and
   for downloading the ubuntu/trusty64 box.
#. **Create the Virtual Machine, Install the Operating System (OS), and
   Install Dependencies**. You can create the Virtual Machine (VM), sync
   the repository to a folder in the VM
   (``/home/vagrant/auvsi_suas_competition``), and execute the automated
   dependency installation. Execute the following commands on the host
   machine:

.. code-block:: bash

    $ vagrant box add ubuntu/trusty64
    $ cd ~/auvsi_suas_competition/setup
    $ vagrant up

Login To the Machine & Open a Terminal
--------------------------------------

Start the dedicated or virtual machine and `open a
terminal <https://help.ubuntu.com/community/UsingTheTerminal>`__. This
is where you will enter commands to begin automated setup.

Download the Repository onto the Machine
----------------------------------------

Please refer to the instructions to :doc:`Download the Repository <downloading>`
onto the machine.

Automated System Setup
----------------------

The AUVSI SUAS competition system uses automated scripts and
:doc:`/prerequisites/puppet` to install system dependencies. Teams should
repeat this step any time they synchronize with the Github repository. The
automated setup script contains more than just the minimal dependencies, it
also includes dependencies that are likely to be needed at some point in the
future.  Teams should execute the following commands to launch the automated
setup:

.. code-block:: bash

    $ cd ~/auvsi_suas_competition/setup
    $ ./setup.sh

Manual Database Setup
---------------------

The AUVSI SUAS competition server relies on a `SQLite
database <http://www.sqlite.org/>`__ to keep durable state that persists
between system restarts. The user must setup the database and give it a
superuser before the system can be used.

The automated setup scripts backup any existing databases and create the
database. Thus you do not need to create the database manually. Should
you desire to create the database manually, to configure a different
admin, then execute the following commands to setup the database. During
the setup process you will be prompted to input a superuser username and
password. Make sure to write this password down! For testing purposes,
the competition recommends using the username "testadmin" and password
"testpass". Future documentation will use these credentials.

.. code-block:: bash

    $ cd ~/auvsi_suas_competition/src/auvsi_suas_server
    $ python manage.py syncdb
