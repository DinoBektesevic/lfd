"""
The results package was designed to help with inspection and analysis of resu-
lts outputted by detecttrails package. Main purose of the package is to allow
for easy and interactive inspection of the results.

It is written using SQLAlchemy, a Python SQL toolkit and a ORM. Because of this
before beginning to work with the module it is neccessary to create, or connect
to, a database. See `connect2db` function from this module or the `setup_db`
from lfd library root to see how. The underlaying database will, or has to,
have the following schema: 

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
| | * _x1      Float             | | * cd12    Float       |  
| | * _y1      Float             | | * cd21    Float       |  
| -------------------------------- | * cd22    Float       |  
| |         Point p2             | | * t       BasicTime   |
| | * _x2      Float             | | ------------          |
| | * _y2      Float             | | |  events  |          |
| -------------------------------- | ------------          |
| |         LineTime lt          | |                       |
| | * start_t  Float             | |                       |
| | * end_t    Float             | |                       |
| -------------------------------- |                       |
------------------------------------------------------------

Event describes the occurance of a single line on a Frame. A Frame is the SDSS
frame on which at least one Event (linear feature) was registered. If no Event
is associated to a particular Frame, that Frame should be removed from the DB.
No event can exist without there being a Frame associated with it. This consti-
tutes a One-To-Many relationship from Frames to Events and Many-To-One reversed
Events ->|------- Frame
Frame  -|------<- Events

The awkward notation of the tables reflects the ORM aspects of the DB. The re-
lationships 'frame' and 'events' can be accessed as attributes of the class
that map onto their respective tables. This allows for simpler, more object
oriented access to immediatelly related objects.
Point is another special SQLAlchemy construct (a mutable composite) that allows
us to map several columns to a single object, again allowing for a more object
oriented interface.
The SQL type BasicTime was implemented to allow for more powerful astronomy
focused date and time management. It is essentially the SDSS modified TAI time-
stamp stored as a Float value in the DB but wrapped in Astropy's Time object.

By default, the used SQL database that will be used is assumed to be SQLite but
this is not mandatory. In fact users are encouraged to connect to other DBs,
prefferencially one that enforces referential integrity to avoid loss of
consistency.

TODO: MetaEvent - when an object passes over the entire CCD array it creates a
lot of Events, but is still the same object. A MetaEvent table linking multiple
Events into a singular object is still required. 

  Usage
-------------
This is not a tutorial on the full usage of SqlAlchemy, DB's or on how to write
queries that return your desired data.

The tables and metadata will be registered on import.
>>> from lfd import results

To connect to an existing DB, specify its URI
>>> results.connect2db(uri="sqlite:////home/user/Desktop/bar.db", echo=False)

Creating a new DB is done the same way. As long as the file at the URI location
does not exist the DB will be created and connected to. By default the conne-
ction is attempted to URI: 'sqlite:////home/$USER/Desktop/foo.db'. Additionally
if the used DB is SQLite, PRAGMA FOREIGN_KEYS is set to ON and echo is True.
>>> results.connect2db()

Calling `create_test_sample` function from the utils module of results package
will populate the newly created DB with some example data.
>>> results.create_test_sample()

Results module will have by now bound a sessionmaker to the name Session.
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
There is, in essence, nothing that can be done by managing your own Session and
could not be done using the context manager. There are, however, several issues
that can arise when not using the context manager. Understanding that intera-
ctivity is easier when real-time inspection of data is possible, both types of
access are allowed and users are urged to close out their sessions as soon as
they are done with them.

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

** A very imporant note: **
There are three different things to be aware of when using SQLAlchemy: the
Engine, Connection and the Session. There should be only one engine per DB URI.
That engine is created and made availible after the call to the `connect2db`
function. A string SQL can be executed is accepted by the Engine or Connection. 

To facilitate a more OO type of interaction SQlAlch offes a different approach.
A Session is a factory, the purpose of which is, when called, to create a
Session object. Since the same factory will create our Session objects it is
guaranteed that all Sessions will have the same configuration. Through Session
we can add, delete or construct Query objects to interact with the DB through
Session's current Connection. Sessions sound like a step extra to just using
Connection, and a session_scope sounds like yet another step to just get to
Session, but there are several advantages to them:
* automatic construction of SQL queries from OO like expressions
* guaranteed connection creation and release (? hopefully)
* Identity map
* Unit of Work pattern

There are some downsides attached to this approach. The biggest one is the loss
of ability of live inspection of data through prompt or IDLE. Data is accessi-
ble only from within the scope. This complicates interactivity quite a bit -
even if it is the correct way to do this. Another downside is that related
objects won't neccessarily be loaded into identity map because of lazy load.
This produces the following examples when results module behaves
inconsistently/is being used incorrectly:

EX1: Lazy load 
>>> with results.session_scope() as s:
        e = s.query(results.Event).first()
>>> e
Traceback : sqlalchemy.orm.exc.DetachedInstanceError

* Incorrect use: session scope is meant to be used as a Unit of Work pattern,
                grouping multiple operations into a single transaction, outside
                of that session scope all additional database operations should
                not be possible.
* Inconsistency: Primary purpose of the reusults package is to offer users inte
                ractive introspection of data, data queried by this method will
                not be availible outside of the scope (i.e. prompt, or IDLE).
                The data does not live outside the scope, very hard to inspect
                interactively.

EX2:
>>> e = results.Event.query().first()
>>> e
<lfd.results.event.Event .... object>

* Inconsistency: The "shortcut" query on the mapped objects themselves returns 
                 a query object. Each Query object will carry with itself their
                 own Session object, each of which will have their Connection
                 object factory. This makes it possible to get the data in an
                 explorative/interactive way but it breaks the UoW pattern and
                 could potentially be dangerous to use (depending mainly on the
                 type of SessionPool).
"""
from os import path
#from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy import create_engine as _create_engine
import sqlalchemy

__query_aliases = {
    "Event" : "events",
    "Frame" : "frames"
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
               echo=True):
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
