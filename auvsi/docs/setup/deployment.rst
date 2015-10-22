Deployment
==========

The competition server will be configured differently at the competition
than during testing. This difference will reflect deployment vs
debugging configurations. Teams do not need to worry about this for
development.

Deployment steps are summarized in the `Deploying Django
Doc <https://docs.djangoproject.com/en/1.7/howto/deployment/>`__.
Deployment of the server consists of:

#. **Configuring & Enabling Apache**. The server will be deployed with
   the Apache web server. This will increase performance of the web
   server directly. Requests will flow through the Apache server and
   then passed to the Django application.
#. **Changing the Secret Key**. This is a secret key that is used for
   encryption purposes. Teams will not know this during the competition
   for security reasons. It will be changed to a large and
   cryptographically random value.
#. **Disabling Debug Mode**. Disabling debug mode will strip error and
   debug information from the displays the teams see. It will also
   enable performance optimizations that are otherwise disabled during
   testing for debugging purposes.

The judges will also be running black-box and white-box monitoring, some
of which will involve additional computers. These will not be supplied
to the teams for testing. The judges will also be configuring the router
and computers to isolate network traffic.
