Prerequisites
=============

This section discusses the prerequisite knowledge needed to develop,
manage, and deploy the AUVSI SUAS Competition server. Teams should learn
these base systems before attempting to use or understand the AUVSI SUAS
Competition system. The underlying systems are as follows:

#. Creating the Machine

   #. **Install on a Device**. This method involves installing Ubuntu as
      the base/host Operating System (OS) instead of as the guest
      operating system. This choice has the highest performance, is the
      slowest to setup, and requires dedicated hardware. This is the
      recommended method.
   #. :doc:`virtualbox`.
      VirtualBox is an application that can be used to run virtual
      machines. Virtual machines can be used to run a separate operating
      system on top of a host operating system, or the native operating
      system. The competition server requires Ubuntu, which may not be
      the host operating system. A virtual machine, run by VirtualBox,
      can be used to run Ubuntu.
   #. :doc:`vagrant`.
      Vagrant is a system to automatically create and manage development
      environments. This saves on the hassle of creating Virtual
      Machines and launching setup scripts.

#. :doc:`ubuntu`.
   Ubuntu 14.04 LTS is the operating system supported by the competition
   server. This operating system is a distribution of Linux.
#. :doc:`git`.
   Git is a software version control system. Git is similar to systems
   like CVS, Mercurial, Perforce, SVN, and Team Foundation Server. Git
   hosts the source code for many systems, and is best known for hosting
   open source systems on `Github <https://github.com/>`__. Git is a
   distributed source control system and enables local revision control.
#. :doc:`puppet`.
   Puppet is an IT automation system which can be used to install
   dependencies, install software, and configure a system. Puppet is
   used by the repository to initialize the base Ubuntu operating system
   with dependencies.
#. :doc:`python`.
   Python is the programming language used to implement the AUVSI SUAS
   competition server.
#. :doc:`django`.
   Django is the underlying web server which powers the AUVSI SUAS
   competition server. This system provides request handling, URL
   mapping, an Object Relational Mapper (ORM), automated testing, and
   much more.

--------------

.. toctree::
   :hidden:

   virtualbox
   vagrant
   ubuntu
   git
   puppet
   python
   django
