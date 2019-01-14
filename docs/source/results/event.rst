Event
=====

.. automodule:: lfd.results.event

In short:

1. Non-prefixed coordinates are properties of the Event class (i.e. x1, y1...).
   The column names are prefixed with an underscore (i.e. _x1, _cx1...)
2. always change column values through properties since many of them have additional
   sanity and caveats checking imposed on them
3. Points interpret the coordinates in frame-referenced mode by default
4. Frame properties can not be changed through Event
5. If Frame is changed the changes won't reflect on Event untill DB commit is made.

Longer explanation:

Point objects handle the coord conversions and maintain consistency among the
coordinates during interactive work. The table values are hot-wired to Point
objects through composites and properties. It is easy to commit a mistake to DB
when working with column attributes directly and leave the DB in inconsistent
state that can't be fixed without manually editing the value.

Point objects are dependent on the Frame object to provide a reference point for
conversion between the two coordinate systems. Frame should update the Event's
coordinates, but this is only enforced at instantiation time. Enforcing
consistency only at instantiation time lets us leave the well-defined CCD coord
system into ccd gaps and then `snap2ccd` before commiting. But at the same time
is possible not to see the changed values update immediately when a Frame
attribute is changed. The coordinates will be updated once a DB commit is made.
Additionally, the Event to Frame relationship is many to one, which means there
can be many events on a Frame. Updating a Frame requires reflecting that change
to all Events on it.

Point objects will issue warnings or errors if inconsistent situations arise.
When a warning is issued, unless it's clearly understood and expected, the best
course of action is to issue a rollback. Otherwise DB could be sent to an
inconsistent state.

The start/end times are stored in the DB in the SDSS-TAI format. There are
some caveats when converting this time to MJD. See: https://www.sdss.org/dr12/help/glossary/#tai

.. autoclass:: lfd.results.event.Event
   :members:
   :private-members:
