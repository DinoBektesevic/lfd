Database and setup
==================

The underlaying database schema looks something like::

 ------------------------------------          -------------------------
 |  events:                         |          |  frames:              |
 ------------------------------------          -------------------------
 |   * id       (autoincrement)     |<--|    |-|-* run     PrimaryKey  |
 | -------------------------------- |   |    |-|-* camcol  PrimaryKey  |
 | |           frame              | |   |    |-|-* filter  PrimaryKey  |
 | | * _run     ForeignKey(frames)|-|---|--->|-|-* field   PrimaryKey  |
 | | * _camcol  ForeignKey(frames)| |   |      | * crpix1  Float       |
 | | * _filter  ForeignKey(frames)| |   |      | * crpix2  Float       |
 | | * _field   ForeignKey(frames)| |   |      | * crval1  Float       |
 | -------------------------------- |   |      | * crval2  Float       |
 | |         Point p1             | |   |      | * cd11    Float       |
 | | * _x1, _cx1   Float          | |   |      | * cd12    Float       |
 | | * _y1, _cy1   Float          | |   |      | * cd21    Float       |
 | -------------------------------- |   |      | * cd22    Float       |
 | |         Point p2             | |   |      | * t       BasicTime   |
 | | * _x2, _cx2   Float          | |   |      | ------------          |
 | | * _y2, _cy2   Float          | |   |------|-|  events  |          |
 | -------------------------------- |          | ------------          |
 | |         LineTime lt          | |          |                       |
 | | * start_t  Float             | |          |                       |
 | | * end_t    Float             | |          |                       |
 | -------------------------------- |          |                       |
 ------------------------------------          -------------------------

`Event` describes the occurence of a single line on a `Frame`. A Frame is the
SDSS frame on which at least one Event (linear feature) was registered. If no
Event is associated to a particular Frame, that Frame should be removed from
the DB.

No event can exist without an being associated toa Frame. This constitutes a
One-To-Many relationship from Frames to Events and Many-To-One in reverse::

 Events ->|------- Frame
 Frame  -|------<- Events

The awkward notation of the tables reflects the ORM aspects of the DB. Many of
the attributes of the first table are marked with an underscore and I would
advise not to access them directly. Even though a lot of effort has been put
into assuring consistency of data no matter what is done to it, dealing directly
with the values assumed understanding of the SDSS' CCD layout and usually comes
with a loss of functionaity.

Instead many wrappers (i.e. Point, BasicTime etc.) are offered around those
attributes that expand on their functionality and ensure data consistency. 

Relationships 'frame' and 'events' can be accessed as attributes of the class.
This allows for simpler, more object oriented access to immediatelly related
objects.

Point is another special SQLAlchemy construct, a mutable composite. Point class
ensures data consistency in an interactive session while managing coordinate
transformations between multiple coordinate systems.

The SQL type BasicTime was implemented to allow for more powerful astronomy
focused date and time management. It is essentially the SDSS modified TAI time
stamp stored as a Float value in the DB but wrapped in Astropy's Time object.

By default, SQL database that will be used is SQLite but this is not mandatory.
Other DBs can be used in its stead, preferentially ones that enforce referential
integrity to avoid loss of consistency.

.. todo::
    MetaEvent - when an object passes over the entire CCD array it creates a
    lot of Events, but is still the same object. A MetaEvent table linking
    multiple Events into a singular object is still required.


Connecting to the DB
====================

The tables and metadata are registered on import. Connecting to the Db and
acquiring an engine, session and connection is done similarly to how setup of
detecttrails module works. All three are availible as module global variables,
but it is recommended that context managers found in utilities module are used.

.. code-block:: python
   :linenos:

   import lfd
   lfd.setup_results(URI="sqlite:///", dbpath="~/Desktop", name="foo.db", echo=False)

Again, as before this functionality is replciated and accessible from the module
itself as well.

.. code-block:: python
   :linenos:

   from lfd import results
   results.connect2db(uri="sqlite:////home/user/Desktop/bar.db", echo=False)

If the DB at the desired URI does not exists a new empty DB is created and
connected to instead. By default the connection is attempted to URI:
`sqlite:////home/$USER/Desktop/foo.db`. Additionally if the used DB is SQLite,
`PRAGMA FOREIGN_KEYS` is set to ON and `echo` is set to False.

If this is not flexible enough a DB can be created manually and the package's
engine and session, availible as attributes of `results` module, can be set to
the engine and session created with that DB directly.

.. autofunction:: lfd.setup_results

.. autofunction:: lfd.results.connect2db
