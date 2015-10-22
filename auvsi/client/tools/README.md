AUVSI SUAS: Sample Interoperability Implementation
================================================================================

This directory contains a sample implementation of interoperability. This
implementation can be used as blackbox monitoring of the running system, to
load test the deployment configuration, or test components which are otherwise
difficult to test.

You can use the code by executing:

    python interop_client.py localhost:80 0.1 testuser testpass

NOTE: This client is deprecated and should not be used for new tools.


## Mission Simulator
The flightsim module can be used to test the system using realistic flight
dyanamics.  The motion of the UAV is determined by the kml file.  An example
file is provided "./data/FlightPath.kml".  The file should contain a line path
called FlightPath.  A suitable path may be created using the "Add Path" icon
in Google Earth.  Altitudes must be added manually when using that process.

    python run_flightsim.py 127.0.0.1:8000 0.1 cornell uni ./data/FlightPath.kml
