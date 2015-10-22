Implementation Hints
====================

This page contains some hints on how to implement interoperability.
These points are common sources of poor performance.

#. **Reuse of TCP Connections**. The HTTP protocol, which is the
   protocol used by the interoperability specification and server,
   operates on top of the TCP protocol. The TCP protocol has an
   initialization and teardown phase that is costly. Teams should open
   one HTTP connection and reuse it between requests, which will keep
   the underlying TCP connection open, and forgo repeatably paying the
   cost of initialization and teardown. `TCP Protocol
   Initialization <http://en.wikipedia.org/wiki/Transmission_Control_Protocol#Connection_establishment>`__.

#. **Profiling of Implementation**. Team's should profile their
   implementation to determine causes of slow execution. Is the limit to
   interoperability execution rate the speed at which the competition
   server responds? Or is it the speed at which UAS telemetry can be
   generated / retrieved? How long does it take to initiate a
   connection? To perform each interoperability part? Etc.

#. **Concurrent Data Generation & Interoperability**. The UAS telemetry
   data should be generated
   `concurrently <http://en.wikipedia.org/wiki/Concurrency_(computer_science)>`__
   with executing interoperability. The required update rate is 10 Hz,
   or to send a request every 0.1 seconds. Let's say the time to
   generate data, which may involve communicating with the autopilot,
   takes ``X`` seconds. Let's also say it takes ``Y`` seconds to execute
   inteorperability by communicating with the server. If you do one
   operation at a time, it will take ``X + Y`` seconds. However, if you
   do them concurrently it will take ``max(X, Y)`` seconds. It may be
   that ``X + Y`` takes longer than 0.1 seconds, whereas ``max(X, Y)``
   takes less than 0.1 seconds. In this competition's deployment, the
   TCP round-trip communication time for interoperability should take
   less than 1 millisecond. Any single interoperability interface should
   take a max of 0.01 seconds (based on load testing). Thus execution of
   interoperability ``Y`` should take at most ``0.001 + 0.01 = 0.011``
   seconds, which is ``8x`` faster than necessary. If your
   implementation takes longer than ``0.1`` seconds, it is likely that
   either you are not performing these operations concurrently, or your
   time to generate / retrieve data ``X`` takes too long.

#. **Status Codes & Debug Output**. The competition server returns
   appropriate status codes and error messages when the server detects
   an error. Your implementation should display these status codes and
   messages so that you can react appropriately to unforeseen problems.

#. **Reliability & Fault Tolerance**. Your code should anticipate many
   types of errors that could occur, detect these situations, react
   automatically, and recover from them. For example, the competition
   server may restart due to some unanticipated problem (e.g. overheated
   computer, someone trips on power cord), in which case the user will
   need to re-login as the session cookie will become invalid. As
   another example, the HTTP connection may reset due to dropped
   packets, and the user may need to reconnect but not necessarily
   re-login. Your software should expect that these events can happen,
   should assume that they will, and have the necessary code to respond.

#. **Nagle's Algorithm**. The TCP protocol has an optimization enabled
   by default called `Nagle's
   algorithm <http://en.wikipedia.org/wiki/Nagle%27s_algorithm>`__. This
   algorithm batches outbound communication to reduce overhead and
   increase bandwidth, at the cost of increased latency. Teams may want
   to disable this on the client side (team's implementation). Teams
   should also pipeline requests when the server does not respond fast
   enough due to artificial latency.
