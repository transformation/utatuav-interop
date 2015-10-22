# Summary
The included files form a basic implementation of a interoperability solution for the Mission Planner ground station software.
It is expected that teams will modify and tailor this application to their system's specific needs and capabilities.

## Usage
The client proxy requires that the python interop client be installed for the instance of python running it.
This may be accomplished by including the interop package on the PYTHONPATH environment variable, or by pip installing
the package to the local instance of python.
The client proxy has a number of options to configure it to correctly connect to the competition server.
These options may be view by running the command:

    python clientproxy.py -h

Once the client proxy is running, the auvsi_mp.py script should be run in Mission Planner's scripting interface.
The stdout of this script should print the server message if everything is working as excepted.
The client proxy will then print out the current telemetry transmission rate and response codes from the server.
The expected response code is "200" if everything is working as expected.
 