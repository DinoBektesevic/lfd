import sqlalchemy as sql

from lfd import results as res
from lfd.results import Event

from . import imagedb
from .imagedb import Image

class Indexer:
    """Generic indexer of items in a database. Given a list of items or a
    database connection, session and table will produce an order-maintained
    list of item ids. Indexer allows us to move through the rows of the db in
    sequentiall or non-sequential manner while loading the currently pointed
    to object dynamically from the database.

      init parameters
    -------------------
    items    - list of unique ids of the objects from the db
    dbcong   - a dictionary containing the following keys and values
               connector :        a callable that takes a URI, creates an
                                  engine to the database, maps the tables and
                                  creates a Session object. Since engine and
                                  Session should persist through the lifetime
                                  of the Indexer these should be declared as a
                                  module global values to which session_manager
                                  can hook to (see imagedb.py or __init__.py of
                                  results module for implementation details)
                session_manager : a context manager for instantiated Session
                                  (see imagedb.py or utils.py of results)
                table           : the ORM class that maps the table(s) in the
                                  database.

      attributes
    -------------------
    current    - current position of the index
    maxindex   - the maximal value of the index
    items      - list of unique ids of db rows, the item[current] points to the
                 currently selected row of the db
    item       - currently selected object, dynamically loaded from the database
    """
    def __init__(self, items=None, dbconf=None):
        self.item = None
        self.items = [None]
        self.current = None
        self.dbconf = {
            "connector": None,
            "session_manager" : None,
            "table" : None
        }

        if items is not None:
            self.items = items
            self.current = 0

        if dbconf is not None:
            self.dbconf = dbconf

        self.maxindex = len(self.items)

    def initFromDB(self, dbURI):
        """Given a db URI connects to it and indexes all rows found in it."""
        db = self.dbconf
        db["connector"](dbURI)
        with db["session_manager"]() as session:
            items = [id for id, in session.query(db["table"].id).all()]
        self.items = items
        self.current = 0
        self.maxindex = len(self.items)
        self.get()

    def __step(self, step):
        """Makes a positive (forward) or negative (backwards) step in the list
        of items and loads the newly pointed to object.
        """
        if self.current == None:
            self.current = None
        else:
            dummyindex = self.current + step
            if dummyindex > self.maxindex:
                self.current = self.maxindex
            elif dummyindex < 0:
                self.current = 0
            else: # 0 < dummyindex < self.maxindex:
                self.current = dummyindex
            self.get()

    def next(self):
        """Makes a step forward and retrieves the item."""
        self.__step(1)

    def previous(self):
        """Makes a step backwards and retrieves the item."""
        self.__step(-1)

    def skip(self, steps):
        """Skips 'steps' number of steps. Value of 'steps' can be positive or
        negative indicating forward or backward skip respectively."""
        tmpnext = self.current + steps
        if 0 <= tmpnext and tmpnext <= self.maxindex:
            self.__step(steps)

    def goto(self, index=None, itemid=None):
        """If an 'index' is provided jumps to the given index. If 'itemid' is
        given, jumps to the index of the provided item id. If neither are given
        reloads the current item.
        """
        steps = 0
        if index is not None:
            steps = index-self.current
        if itemid is not None:
            index = self.items.index(itemid)
            steps = index-self.current
        self.skip(steps)


    def __getFromFrameIds(self, run, camcol, filter, field, which):
        """Given a frame identifier (run, camcol, filter, field), and possibly
        `which`, queries the database for the object and returns it.
        In case multiple objects correspond to the same frame identifier `which`
        selects which of the returned results are desired.
        The returned object is expunged from the database session.
        """
        db = self.dbconf
        with db["session_manager"]() as session:
            query = session.query(db["table"]).filter(db["table"].run==run,
                                                      db["table"].filter==filter,
                                                      db["table"].camcol==camcol,
                                                      db["table"].field==field)
            items = query.all()
            if len(items) > 1:
                item = items[which][0]
            elif len(items) == 1:
                item = items[0]
            else:
                return None

            insp = sql.inspect(item)
            relationships = insp.mapper.relationships.keys()
            for relative in relationships:
                session.expunge(getattr(item, relative))
            session.expunge(item)
        return item

    def __getFromItemId(self, itemid):
        """Given an unique object id queries the database for the row and
        returns it as an appropriate object. The returned object is expunged
        from the database session.
        """
        db = self.dbconf
        with db["session_manager"]() as session:
            q = session.query(db["table"])
            q = q.filter(db["table"].id==itemid)
            item = q.first()
            if item is not None:
                # objects potentially have many relationships that also need to
                # be expunged if we want them to be visible after session.close
                insp = sql.inspect(item)
                relationships = insp.mapper.relationships.keys()
                for relative in relationships:
                    session.expunge(getattr(item, relative))
                session.expunge(item)
        return item

    def get(self, run=None, camcol=None, filter=None, field=None, which=0,
            itemid=None):
        """If nothing is provided, jumps to the current index and loads the db
        row into item. If frame identifiers (run, camcol, filter, field) are
        given loads the object from the database and jumps the index to its
        position. If itemid is provided, loads the desired object and jumps to
        its index.

        In some cases the frame identifiers can be shared among multiple rows
        (i.e. multiple Events on a Frame) in which case providing 'which' makes
        it possible to select a particular item from the returned set.
        """
        if all([run, camcol, filter, field]):
            item = self.__getFromFrameIds(run, camcol, filter, field, which)
            if item is not None:
                self.goto(itemid=item.id)
        elif itemid is not None:
            item = self.__getFromItemId(itemid)
            if item is not None:
                self.goto(itemid=itemid)
        else:
            itemid = self.items[self.current]
            item = self.__getFromItemId(itemid)

        self.item = item


class EventIndexer(Indexer):
    """Indexes Events database providing a convenient way to establish order
    among the items.
    """
    def __init__(self,  URI=None):
        super().__init__()
        self.dbconf = {
            "connector" : res.connect2db,
            "session_manager" : res.session_scope,
            "table" : Event
        }

        if URI is not None:
            self.initFromDB(URI)

    @property
    def event(self):
        """Returns the event pointed to by the current index."""
        return self.item

    def commit(self):
        """Add the object back to the session and commit any changes made to it."""
        self.event.verified = True
        with res.session_scope() as session:
            session.add(self.event)
            session.commit()


class ImageIndexer(Indexer):
    """Indexes Image database providing a convenient way to establish order
    among the items.
    """
    def __init__(self,  URI=None):
        super().__init__()
        self.dbconf = {
            "connector" : imagedb.connect2db,
            "session_manager" : imagedb.session_scope,
            "table" : Image
        }

        if URI is not None:
            self.initFromDB(URI)

    @property
    def image(self):
        """Returns the image pointed to by the current index."""
        return self.item
