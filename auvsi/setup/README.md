AUVSI SUAS Interoperability: Setup Scripts
==========================================

This folder contains setup scripts to automatically install dependencies for
development and deployment of the AUVSI SUAS Interoperability Systems.

The automated setup script performs the following actions:
  1. Updates the package list
  2. Ugrades old packages to latest
  3. Installs the puppet package
  4. Downloads puppet modules (e.g. aptitude module)
  5. Launches automated dependency setup via puppet scripts
  6. Backups any existing database
  7. Creates new database with initial test admin
     (username: testadmin, password: testpass)

After setting up the machine, run the `/test.sh` script to run all server and
client tests. This will validate the machine is properly setup.


Vagrant
-------

To automatically build and setup a virtual machine, install
[Vagrant](https://www.vagrantup.com/), change into this directory, and run:

``` sh
vagrant up
```

This will download an Ubuntu base image, boot it and execute the Puppet
manifest. A couple of ports are forwarded from the guest to the host:

* Guest port 80 to host port 8000: An Apache web server running the interop
  server is available on this port.
* Guest port 8080 to host port 8080: To be used when running a development
  server (with `manage.py`).

A single command can be executed on the host to run all tests:

``` sh
vagrant ssh -c "/interop/test.sh"
```


Dedicated Machine or VirtualBox
-------------------------------

To setup a physical or prebuilt virtual machine, change the working directory
to this directory, and execute script:

``` sh
./setup.sh
```
