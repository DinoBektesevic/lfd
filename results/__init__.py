"""
The results package was designed to help with inspection and analysis of resu-
lts outputted by detecttrails package. Main purose of the package is to allow
for easy and interactive inspection of the results.

It is written using SQLAlchemy, a Python SQL toolkit and a ORM. Because of this
before beginning to work with the module it is neccessary to create, or connect
to, a database. See `connect2db` function from this module or the `setup_db`
from lfd library root to see how to do that.

  Database
----------------

The underlaying database schema looks something like:

------------------------------------------------------------
|  events:                         |  frames:              |
------------------------------------------------------------
|   * id       (autoincrement)     | * run     PrimaryKey  |
| -------------------------------- | * camcol  PrimaryKey  |
| |           frame              | | * filter  PrimaryKey  |
| | * _run     ForeignKey(frames)| | * field   PrimaryKey  |
| | * _camcol  ForeignKey(frames)| | * crpix1  Float       |
| | * _filter  ForeignKey(frames)| | * crpix2  Float       |
| | * _field   ForeignKey(frames)| | * crval1  Float       |
| -------------------------------- | * crval2  Float       |
| |         Point p1             | | * cd11    Float       |
| | * _x1, _cx1   Float          | | * cd12    Float       |
| | * _y1, _cy1   Float          | | * cd21    Float       |
| -------------------------------- | * cd22    Float       |
| |         Point p2             | | * t       BasicTime   |
| | * _x2, _cx2   Float          | | ------------          |
| | * _y2, _cy2   Float          | | |  events  |          |
| -------------------------------- | ------------          |
| |         LineTime lt          | |                       |
| | * start_t  Float             | |                       |
| | * end_t    Float             | |                       |
| -------------------------------- |                       |
------------------------------------------------------------

Event describes the occurance of a single line on a Frame. A Frame is the SDSS
frame on which at least one Event (linear feature) was registered. If no Event
is associated to a particular Frame, that Frame should be removed from the DB.
No event can exist without there being a Frame associated with it.
This constitutes a One-To-Many relationship from Frames to Events and
Many-To-One in reversed situation:
    Events ->|------- Frame
    Frame  -|------<- Events

The awkward notation of the tables reflects the ORM aspects of the DB. The re-
lationships 'frame' and 'events' can be accessed as attributes of the class
that map onto their respective tables. This allows for simpler, more object
oriented access to immediatelly related objects.

Point is another special SQLAlchemy construct, a mutable composite. The purpose
of the Point class is to allow user to perserve data consistency in an intera-
ctive session while managing coordinate transformations between multiple coord.
systems.

The SQL type BasicTime was implemented to allow for more powerful astronomy
focused date and time management. It is essentially the SDSS modified TAI time-
stamp stored as a Float value in the DB but wrapped in Astropy's Time object.

By default, SQL database that will be used is SQLite but this is not mandatory.
Other DBs can be used in its stead, preferentially ones that enforce refere-
ntial integrity to avoid loss of consistency.

TODO: MetaEvent - when an object passes over the entire CCD array it creates a
lot of Events, but is still the same object. A MetaEvent table linking multiple
Events into a singular object is still required.

  Usage
-------------
This is not a tutorial on the full usage of SqlAlchemy, DB's or on how to write
queries that return your desired data. This tutorial just showcases some common
practices recommended when using this package.

The tables and metadata will be registered on import.
>>> from lfd import results

To connect to an existing DB, specify its URI
>>> results.connect2db(uri="sqlite:////home/user/Desktop/bar.db", echo=False)

Creating a new DB is done the same way. As long as the file at the URI location
does not exist the DB will be created and connected to. By default the conne-
ction is attempted to URI: 'sqlite:////home/$USER/Desktop/foo.db'. Additionally
if the used DB is SQLite, PRAGMA FOREIGN_KEYS is set to ON and echo is True.

>>> results.connect2db()

If this is not flexible enough a DB can be created manually and the package's
engine and session set to the engine and session created with that DB.

Calling `create_test_sample` function from the utils module of results package
will populate the newly created DB with some example data.

>>> results.create_test_sample()

Results module will have, by now, bound a sessionmaker to the name Session.
Session is used as a staging area for all transactions towards the DB. It is
recommended  that Session is constructed at the beginning of any operation in
which DB access is expected and then immediately closed afterwards:

>>> s = results.Session()
>>> s.query(results.Event).all()
>>> s.close()

If a situation arises in which operation might fail a rollback should be issued

>>> s = results.Session()
>>> frame = results.Frame(2888, 1, "i", 139, 1, 1, 1, 1, 1, 1, 1, 1, 4412911)
>>> s.add_all([frame, frame])
>>> s.commit()
# will fail due to primary key restrictions and s becomes unusable
# to fix it and return to a consistent state:
>>> s.rollback()

Since this is a very common pattern of use when inspecting data results module
has a context manager for the Session that will try to execute an operation and
automatically rollback to a consistent state if it fails and, most importantly,
close the Session:

>>> with results.session_scope() as s:
        s.add_all([frame, frame])

This is not always desireable behaviour, but its use is higly recommended.
There is, in essence, nothing that can be done by managing your own Session
that could not be done using the context manager.

The main purpose of results package is to allow for querying for events and
inspecting their mutual relationships. There are two ways queries can be issued

1) Using the session scope

>>> with results.session_scope() as s:
	    e = s.query(results.Event).first()
        print(e)
        print(e.frame)

or 2) Using one of the query methods

>>> results.Event.query().first()
>>> results.Frame.query().all()

Using Session and session_scope will make sure connections are opened or closed
appropriately. Using <Table>.query method will implicitly open a session and a
connection and carry it along as long as it lives.

...............................................................................
** A very imporant note: **

There are three different things to be aware of when using SQLAlchemy: the
Engine, Connection and the Session. There should be only one engine per DB URI.
Depending on the type of connection pool, there can be 1 or many Connections.
There can always be many Sessions.
The Engine is created and made availible after the call to the `connect2db`
function, usually immediately after importing the module.

One way of executing transactions is via a SQL string sent to the Engine or the
Connection. Another way to execute transactions is by using a Session. There is
a downside to this approach: the loss of real-time interaction with the data in
IDLE or terminal. Users are **ALWAYS** encouraged to use the Session because of
its many other advantages, too long ot go into now but in short:
* a Session is a factory, since the same factory will create our sessions, it
    is guaranteed that all sessions will have the same configuration.
* Session manages its Connections, which otherwise can be hard to do
* automatic construction of SQL queries from OO like expressions
* guaranteed connection creation and release
* Identity map
* Unit of Work pattern

With that in mind see the 'Common misuse patters' section and the source code
of utils.py module from the results package.
...............................................................................

Moving on: queries can be 'filtered' to select results contrained by some
parameters. Selecting all Events with known line start time (s is Session):

>>> s.query(Event).filter(Event.start_t != None).all()

Counting the total number of Events in our DB:

>>> s.query(Event).count()

Counting the number of Frames that have one or more linear feature on them in,
f.e., run 2888

>>> s.query(Frame).filter(Frame.run == 2888).count()

Querying the Session will require the user to explicitly specify a join when
one is needed. The <Table>.query method will perform a join implicity - it is
assumed that during interactive work users want *all* of the selected data to
be availible to them.

>>> s.query.(Event).join(Frame)
>>> Event.query()

Joins are neccessary when querying with conditions on columns from another
table:

>>> s.query(Event).join(Frame).filter(Frame.run == 2888).all()
>>> Event.query("Frame.run == 2888").all()

Querying on time can be a trickier concept. Comparisons with an Astropy Time
object or SDSS TAI time as float number are supported only. This is required
because of the achievable timestamp precission for the linear feature times,
annoying SDSS modified TAI time and overall abundance of different formats.

>>> from astropy.time import Time
>>> t = Time('2005-08-23 17:46:40.000')
>>> s.query(Event).join(Frame).filter(Frame.t > t).all()
or
>>> s.query(Event).join(Frame).filter(Frame.t > 4600000000).all()

These examples should cover most of the situations. 

  Common misuse patterns
-------------------------

EXAMPLE 1:
***********

Wrong:

>>> with results.session_scope() as s:
        e = s.query(results.Event).first()
>>> e.run
Traceback : sqlalchemy.orm.exc.DetachedInstanceError

* Incorrect use: session scope is meant to be used as a Unit of Work pattern,
                grouping multiple operations into a single transaction. Outside
                of that session scope all additional database operations should
                not be possible.
* Inconsistency: Primary purpose of the reusults package is to offer users inte
                ractive introspection of data, data queried by this method will
                not be availible outside of the scope (i.e. prompt, or IDLE).
                The data does not live outside the scope, very hard to inspect
                interactively.

Correct:

>>> with results.session_scope() as s:
        e = s.query(results.Event).first()
        e.run

or if objects want to be inspected interactively in real-time

>>> e = results.Event.query().first()
>>> e.run


EXAMPLE 2:
************

Wrong:

    <in a script, where no real-time interaction is required>
    <some code>
    e = results.Event.query().first()
    <some additional code, perhaps even changing e>

* Inconsistency: The "shortcut" query on the mapped objects themselves returns
                 a query object. Each Query object will carry with itself their
                 own Session object, each of which will have their Connection
                 object factory. This makes it possible to get the data in an
                 explorative/interactive way but it breaks the UoW pattern and
                 could potentially be dangerous to use (depending mainly on the
                 type of SessionPool). It will certanly not be commited to the
                 DB implicitly. See source code of utils.py module for example.

Correct:

    <in a script, where no real-time interaction is required, and the Events>
    <are not modified, but values still are required>
    <some code>

    with results.session_scope() as s:
        e = s.query(results.Event).first()
        x1, x2 = e.x1, e.x2
    <some further code using x1, x2>

or if modification of DB data is required:

    <code calculating new values of x1, x2>
    with results.session_scope() as s:
        e = s.query(results.Event).first()
        e.x1, e.x2 = x1, x2
    <some further code>

EXAMPLE 3:
************

Wrong:

>>> e = s.query(Event).filter(Frame.run == 2888).all()
>>> len(e)
26600

Correct:

>>> e = s.query(Event).join(Frame).filter(Frame.run == 2888).all()
>>> len(e)
10
"""
from os import path
#from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy import create_engine as _create_engine
import sqlalchemy

__query_aliases = {
    "Event" : "events",
    "Frame" : "frames",
    "x1"    : "_x1"   ,
    "y1"    : "_y1"   ,
    "x2"    : "_x2"   ,
    "y2"    : "_y2"   ,
    "cx1"   : "_cx1"  ,
    "cy1"   : "_cy1"  ,
    "cx2"   : "_cx2"  ,
    "cy2"   : "_cy2"
}

Base = _declarative_base()

from .event import *
from .frame import *
from .point import *

from .basictime import *
from .ccd_dimensions import *
from .coord_conversion import *


Session, engine = None, None
def connect2db(uri="sqlite:///"+path.join(path.expanduser("~"), "Desktop/foo.db"),
               echo=False):
    """Connects to an existing DB or creates a new empty DB to connect too.
    The DB has to be mappable by the results package.

      Parameters
    --------------
    URI : an URI used to connect to a DB. By default set to:
        'sqlite:///$USER_HOME/foo.db'.
    name : the name of the existing, or newly created, DB. Default: 'foo.db'
    echo : verbosity of the DB. False by default.
    """
    global Session, engine

    # create the engine that hooks to an existing or creates a new DB
    engine  = _create_engine(uri, echo=echo)
    if uri[:5] == "sqlite":
        engine.execute("PRAGMA FOREIGN_KEYS=ON")

    # map to existing or create new tables in the DB
    Base.metadata.create_all(engine)

    # create a Session object so transactions can be made
    Session = _sessionmaker(bind=engine)

from .utils import *

del event, frame, point, basictime
del ccd_dimensions, coord_conversion
del path
