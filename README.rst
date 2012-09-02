=======================================================
GC Analyser: A Java Garbage Collection Logfile Analyser
=======================================================

What is it?
===========

The GC Analyser project provides a tool built on top of Google App Engine for analysing Java Virtual Machine garbage collector logfiles.

The live deployment will be publicly available shortly at

http://gcanalyser.appspot.com/

Supported JVMs
==============

At present only tested on Oracle Java 6 JVM GC logs with the following garbage collectors:

  * Young Copy and Old MarkSweepCompact
  * Young PS Scavenge Old PS MarkSweep
  * Young ParNew Old MarkSweepCompact
  * Young ParNew Old ConcurrentMarkSweep
  * Young Copy Old ConcurrentMarkSweep

License
=======

BSD

Screen captures
===============
.. image:: gc-analyser/blob/master/screencapture.png
