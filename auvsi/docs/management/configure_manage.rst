Configure & Manage the Server
=============================

Admin Interfaces
----------------

There are two admin interfaces which can be used to configure and manage the
server. One is developed by the AUVSI SUAS Competition judges, the other is
provided by the Django web framework.


SUAS Admin Interface
^^^^^^^^^^^^^^^^^^^^

The SUAS Admin Interface can be reached at the path `/` (e.g.
`http://localhost/`). The first time an admin navigates to this page he or she
will be prompted to login. Once logged in, the admin will be directed to the
mission listing page.

The SUAS admin pages have a navigation bar on top with two headings: "System"
and "Mission". The "System" heading has links pertaining to system-wide
management, and the "Mission" heading has links specific to the mission being
viewed.

#. **System**

   #. **Live View (KML)**. Downloads a KML file which can be opened in Google
      Earth to view real-time information. This provides a visualization
      that complements the one provided in this interface.
   #. **Evaluate Teams (CSV)**. Evaluates the teams and downloads a CSV file.
      This data can be used to determine whether teams completed certain
      tasks. The evaluation is performed for the single active mission.
   #. **Export Data (KML)**. Downloads a KML file which can be opened in Google
      Earth to view the UAS telemetry and other mission data after the
      mission is completed.
   #. **Edit Data**. Opens the Django Admin Interface which can be used to
      configure missions and view raw data.
   #. **Clear Cache**. Caching is used to improve performance of certain
      operations. The caches automatically expire, so users shouldn't need
      to use this, but data modification mid-mission may require explicit
      clearing to react faster.

#. **Mission**

   #. **Evaluate Teams (CSV)**. Evaluates the teams for the mission being
      viewed. This is otherwise the same as the System link.

The mission specific page is broken into two sections. The left side contains a
status indicator, and the right side contains a live map view. The status
indicator shows which teams are sending UAS telemetry and which teams are
listed as "in-flight" (explained below). The data will be colored orange
(warning) if only one is true. The data will be colored green (expected) if
both are true. The live map view shows the major competition elements, the UAS
which is communicating telemetry, and the obstacle positions.


Django Admin Interface
^^^^^^^^^^^^^^^^^^^^^^

The Django Admin Interface can be used to create, view, edit, or delete the
underlying objects in the server's database. This must be used directly to
create a mission configuration. See the `Django Documentation
<https://www.djangoproject.com/>`__ for more information on how to use this
interface.

This interface can be reached through the SUAS Admin interface navigation bar,
or you can navigate directly to `/admin`.


Mission Configuration
---------------------

Prior to the competition, judges will create a MissionConfig (mission
configuration) which defines how the server will behave while teams are
interfacing with the server. The server can store multiple missions at one
time, and uses the "active" mission during a mission demonstration.

Creating, viewing, editing, or deleting a configuration is done in the Django
Admin Interface. Refer to Django Documentation for how to use the interface.


Model Objects
^^^^^^^^^^^^^

#. **GpsPosition**. Latitude and longitude.
#. **AerialPosition**. GPS position and altitude (in MSL).
#. **Waypoint**. Aerial position, and an order number that specifies the
   waypoint's position in a path.
#. **ServerInfo**. The server information returned to users as part of
   the interoperability task. Consists of a timestamp and message for
   the teams.
#. **ServerInfoAccessLog**. A log containing the timestamps and users
   which have made requests for server information.
#. **StationaryObstacle**. A GPS position for the centroid, and the
   radius/height of the cylinder defining the obstacle. This data will
   be returned as part of the interoperability task.
#. **MovingObstacle**. An obstacle speed, a radius for the obstacle's
   sphere, and a set of waypoints defining the obstacle's path.
#. **ObstacleAccessLog**. A log containing the timestamps and users
   which have made requests for obstacle information.
#. **UasTelemetry**. UAS telemetry that is uploaded to the server by
   teams as part of the interoperability task.
#. **FlyZone**. Specifies a valid region for which a UAS can fly. If a
   UAS is not contained within any FlyZone, then the UAS is out of
   bounds.
#. **MissionConfig**. The various settings which define a mission
   configuration. There should only be one defined for the competition.
#. **Users**. The users of the system. There will be one superuser which
   can login to the admin panel and change settings. At the competition
   this superuser will be the judges. There will also be one user for
   each team at the competition, each with a unique username and
   password. Users will authenticate against this information to verify
   identity.


Create a MissionConfig
^^^^^^^^^^^^^^^^^^^^^^

The user must create a MissionConfig in order to test interoperability.

#. On the Django Admin Interface page (`/admin`), click `Mission configs`.
#. Click `Add mission config`.
#. `Is active` defines whether this specific config is the single active
   mission. The active mission is used when responding to requests or storing
   data. The admin must make sure there is only one labeled active at a time.
#. `Home pos` defines the home position. This is the center of the admin
   display and should be where the ground station is.
#. `Fly zones` define the valid areas where a UAS is considered in-bounds. This
   must include the takeoff and landing strip. This is used to evaluate time
   spent out of bounds.
#. `Mission waypoints` define the waypoints the UAS must navigate to during the
   mission. This is used to determine whether the UAS was within the threshold
   distance to consider it satisfied.
#. `Server info` defines the information supplied for the interoperability
   task.
#. `Stationary obstacles` defines the stationary obstacles the UAS must avoid.
#. `Moving obstacles` defines the moving obstacles the UAS must avoid.
#. There are other fields which should be defined. At present they may only be
   used for display purposes.
#. Once the MissionConfig is fully defined, click Save.


Editing a MovingObstacle
^^^^^^^^^^^^^^^^^^^^^^^^

Moving obstacles are defined by waypoints and a speed. To determine the
position of the obstacle at any given time, a spline is evaluated for the given
waypoint set and speed. If the waypoint set or speed is changed, the spline
will be changed, and the position of the obstacle over time will change. For
this reason, once a team mission demonstration starts, the MovingObstacle
configuration should not be changed. Otherwise, the team could see a different
position than that which they are evaluated against.


Mission Management
------------------

Teams are evaluated during the course of flight periods. For example, teams are
required to communicate at 10Hz while the UAS is airborne. The interoperability
system cannot detect that a team is airborne but not communicating, so judges
must explicitly mark when the UAS takes off and lands. This is done by creating
`Takeoff or landing events`. Admins must select which team the event applies
to, whether the UAS is now in the air or not, and on save it marks the time.
This is done via the Django Admin Interface. When a team takes off, an event is
created. When the team lands, another event is created. Multiple flight periods
can be logged for a single team and mission.

The SUAS Admin Interface shows which teams are marked as in flight, and which
teams are uploading UAS telemetry. The status is displayed green if both are
occuring, which is the expected case. The status is displayed orange for the
unexpected case where only one is occuring. A team may upload UAS telemetry
while not flying, so this in itself is not a problem, but it may remind the
judge to mark a team in flight. A team may be in flight and not uploading
telemetry, but this indicates the team is not meeting the requirement.


Mission Evaluation & Export
---------------------------

The interoperability server can automatically evaluate whether the UAS
completed certain tasks. This can be accessed from the SUAS Admin Interface.
The data is downloaded as a CSV file which can be opened in programs like Excel
and Google Sheets.

The interoperability server can also export the data as a KML file, which can
be loaded into Google Earth to visualize the data that was uploaded or
generated.
