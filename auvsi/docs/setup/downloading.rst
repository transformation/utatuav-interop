Downloading the Repository
==========================

Download via Git
----------------

Teams can download the repository by cloning the AUVSI SUAS competition Git
repository hosted on Github. Execute the following commands to clone the
repository into the `home directory
<https://help.ubuntu.com/community/HomeFolder>`__:

.. code-block:: bash

    $ sudo apt-get -y install git
    $ cd ~/
    $ git clone https://github.com/auvsi-suas/interop.git

Syncing Downloaded Code with Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Changes to the system on the Git repository will be changed to fix bugs, add
features, etc. Teams can synchronize their local copy of the system with the
repository's copy by executing the following code:

.. code-block:: bash

    $ cd ~/auvsi_suas_competition
    $ git pull

Download via Website as ZIP File
--------------------------------

Alternatively, you can download go to the `Github Repository Page
<https://github.com/auvsi-suas/interop>`__ and click "Download Zip". Unzip the
contents and place the "auvsi\_suas\_competition" folder in the home directory.
If you download it as a ZIP file, rather than using Git directly, synchronizing
the system with the repository will require you to re-download, unzip, and
replace the folder. Make sure to backup any databases you have created before
synchronizing.
