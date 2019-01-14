Examples
========

This is not a tutorial on the full usage of SqlAlchemy, DB's or on how to write
queries that return your desired data. This tutorial just showcases some common
practices recommended when using this package.

Basic access
------------

Connect to a new database with and populate it with some test sample data (see
:func:`~lfd.results.utils.create_test_sample`)

.. code-block:: python
   :linenos:

   from lfd import results
   results.connect2db("~/Desktop/foo.db")
   results.create_test_sample()

Results module will have, by now, bound a sessionmaker to the name `Session`.
Session is used as a staging area for all transactions towards the DB. It is
recommended  that Session is constructed at the beginning of any operation in
which DB access is expected and then immediately closed afterwards:

.. code-block:: python
   :linenos:

   s = results.Session()
   s.query(results.Event).all()
   s.close()

Rolling back the changes
------------------------

If a situation arises in which operation might fail a rollback should be issued

.. code-block:: python
   :linenos:

   s = results.Session()
   frame = results.Frame(2888, 1, "i", 139, 1, 1, 1, 1, 1, 1, 1, 1, 4412911)
   s.add_all([frame, frame])
   s.commit()

   # will fail due to primary key restrictions - same frame added twice
   # this renders the session unusable. To fix it issue a rollback:
   s.rollback()
   s.close()

Session context manager
-----------------------

Since open-commit-rollback-close is a very common pattern of use when inspecting
data, results module has a context manager (see :func:`~lfd.results.utils.session_scope`)
for the Session that will return an opened session, commit the changes made to
objects while it was opened and automatically close it at the end of the block.
If a problem was encountered, a rollback is automatically issued.

.. code-block:: python
   :linenos:

   with results.session_scope() as s:
       s.add_all([frame, frame])

There is, in essence, nothing that can be done by managing your own Session
that could not be done using the context manager. The downside of context
managers is the fact that objects fetched by, but not expunged from, the session
will not be availible after the session closes. 

Adding and expunging objects
----------------------------

Expunging loads objects data and detaches it from the session, which allows it
to be used after the session has closed. Expunged objects can be manipulated and
have their values changed but if they are not added back to the session the
changes will not persist.

.. code-block:: python
   :linenos:

   with results.session_scope() as s:
      frame = s.query(results.Frame).first()
   # will raise an DetachedInstanceError
   frame

   with results.session_scope() as s:
      frame = s.query(results.Frame).first()
      s.expunge(frame)
   # will not raise error
   frame
   # will raise an error
   frame.events

If access to the object(s) relationships is needed then that relationship has to
be expunged as well. Note: Event uses Frame in its repr string, ergo it must not
be printed or an error will be raised. In the same lines, expunging `frame.events`
will raise an error as it's a list of `Event` objects, not an `Event` object
itself.

.. code-block:: python
   :linenos:

   # when working with single InstrumentedAttribute 
   with results.session_scope() as s:
      event = s.query(results.Event).first()
      s.expunge(event.frame)
      s.expunge(event)
   # will not raise error
   event
   event.frame

   # loading the entire InstrumentedList has a workaround
   with results.session_scope() as s:
      frame = s.query(results.Frame).first()
      _ = frame.events
      s.expunge_all()
   # will not raise an error
   frame
   frame.events

   # make a change and persist it in the DB
   frame.events[0].x1 = 999
   with results.session_scope() as s:
      s.add_all(frame.events)
      s.add(frame)

The frames workaround works by forcing non-lazy load of all associated events
into the session - therefore `expunge_all` will work. Constantly expunging can
be a bit tiresome the :func:`~lfd.results.utils.deep_expunge` and
:func:`~lfd.results.utils.deep_expunge_all` can be used to expunge all first
level relationships of given item/s, sometimes.

Querying
--------

The main purpose of results package querying for events and inspection of their
mutual relationships. There are two ways queries can be issued, one was just
shown in the examples above

1) Using the session scope

   .. code-block:: python
      :linenos:

      with results.session_scope() as s:
          e = s.query(results.Event.run).first()
          print(e)
          print(e.frame)

2) Using one of the query methods

   .. code-block:: python
      :linenos:

      results.Event.query("frames.run==2888").first()
      results.Frame.query("frame.t>4702185918").all()

Using Session and session_scope will make sure connections are opened or closed
appropriately. Using `<Table>.query` method will implicitly open a session and a
connection and carry it along as long as it lives.

The second method has no particular real benefit, in fact it only has negatives,
compared to the first, except that it's faster to type when interactively
experimenting with the data in the terminal/idle/etc. Because it skips both the
filter and the session scope statements. It also accepts string-like SQL queries
and performs an implicit join between the tables so even the complicated queries
can be written quickly. I discourage the use of this approach, except sometimes
in interactive use, for various reasons some of which are described bellow.

.. attention::

   There are three different things to be aware of when using SQLAlchemy:

   * the `Engine`,
   * the `Connection`,
   * and the `Session`.

   There should be only one engine per DB URI. Depending on the type of connection
   pool, there can be 1 or many Connections. There can always be many sessions.
   
   The Engine is created and made availible after the call to the :func:`~lfd.connect2db`,
   usually immediately after importing the module. Session is a factory that
   will create a session when called (i.e. `Session()` from early examples).
   Users are **ALWAYS** encouraged to use the Session because of its many
   advantages, but mainly because, as stated above, there can be many or just 1
   Connection that is shared among many sessions. If not properly managed, and
   it is hard to properly manage, errors occur. Alongside that very important
   fact, there are some other benefits:
   
   * a Session is a factory, since the same factory will create our sessions, it
     is guaranteed that all sessions will have the same configuration.
   * Session manages its Connections, which otherwise can be hard to do
   * automatic construction of SQL queries from OO like expressions
   * guaranteed connection creation and release
   * Identity map
   * Unit of Work pattern
   
   For more, see: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html 

Queries can be 'filtered' to select results contrained by some parameters.

   .. code-block:: python
      :linenos:

      with results.session_scope() as s:
          # Selecting all events from specific run 
          s.query(Event).filter(Event.run=2888).all()

          # same query as previous section, example 2 - querying Event on Frame
          # attribute requires join
          query = s.query(lfd.results.Event).join(lfd.results.Frame)
          fquery = query.filter(lfd.results.Frame.t > 4702185918)
          f = fquery.all()

          # a demo on why this is still better than querying tables directly

          # Selecting all Events with known line start time
          s.query(Event).filter(Event.start_t != None).all()

          # selecting by using human readable data formats
          fquery = query.filter(lfd.results.Frame.t.iso > '2009-09-27 10:06:10.430')
          f = fquery.all()
          results.deep_expunge_all(f, s)

Many attributes, like the `BasicTime` in Frame, have wrappers that allow them to
be used more expressively and clearly in the code. That is why their use is so
heavily recommended. By using them you don't have to know about the
implementation details and caveats. Counting the total number of Events in
results DB:

   .. code-block:: python
      :linenos:

      s.query(Event).count()

These examples should cover most of the situations.
