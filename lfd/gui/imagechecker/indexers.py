"""Indexers establish order amongs items 
"""
import sqlalchemy as sql

from lfd import results as res
from lfd.results import Event

from lfd.gui.imagechecker import imagedb
from lfd.gui.imagechecker.imagedb import Image

class Indexer:
    """Generic indexer of items in a database. Given a list of items or a
    database connection, session and table will produce an order-maintained
    list of item ids. Indexer allows us to move through the rows of the db in
    sequentiall or non-sequential manner while loading the currently pointed
    to object dynamically from the database.

    Parameters
    ----------
    items : list, tuple
      list of unique ids of the objects from the db

    Attributes
    ----------
    current : int
      current position of the index
    maxindex : int
      the maximal value of the index
    items : list
      unique ids of DB rows, the item[current] points to the currently selected
      row of the DB
    item : object
      currently selected dynamically loaded from the DB as an object

    """
    def __init__(self, items=None):
        self.item = None
        self.items = [None]
        self.current = None

        if items is not None:
            self.items = items
            self.current = 0

        self.maxindex = len(self.items)
        # loads the first item into self.item, if possible
        self.get()

    def initFromDB(self, dbURI):
        """Connects to the given DB URI and indexes wanted rows from it."""
        raise NotImplementedError(("The implementations needs to be defined "
                                   "by a specific child class."))

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
        negative indicating forward or backward skip respectively.

        """
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

    def _getFromFrameId(self, *args, **kwargs):
        """Given a frame identifier (run, camcol, filter, field), and possibly
        `which`, queries the database for the object and returns it. Should be
        implementation specific perogative of classes that inehrit from Indexer

        """
        raise NotImplementedError(("Implementation needs to be defined by a "
                                   "specific child class."))

    def _getFromItemId(self, *args, **kwargs):
        """Given an unique object id queries the database for the row and
        returns it as an appropriate object. The returned object is expunged
        from the database session.

        """
        raise NotImplementedError(("Implementation needs to be defined by a "
                                   "specific child class."))

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

        The selected item is expunged from the session.

        Parameters
        -----------
        run : int
          run identifier
        camcol : int
          camcol identifier
        filter : str
          string identifier
        field : int
          field identifier
        which : int
          if multiple items are returned, which one in particular is wanted
        itemid : int
          unique id of the desired item

        """
        if all([run, camcol, filter, field]):
            item = self._getFromFrameId(run, camcol, filter, field, which)
            if item is not None:
                self.goto(itemid=item.id)
        elif itemid is not None:
            item = self._getFromItemId(itemid)
            if item is not None:
                self.goto(itemid=itemid)
        else:
            if self.current is None:
                item = None
            else:
                itemid = self.items[self.current]
                item = self._getFromItemId(itemid)

        self.item = item


class EventIndexer(Indexer):
    """Indexes Events database providing a convenient way to establish order
    among the items.

    """
    def __init__(self,  URI=None):
        super().__init__()

        if URI is not None:
            self.initFromDB(URI)

    def initFromDB(self, uri):
        """Connects to a database and indexes all Events therein."""
        res.connect2db(uri)
        with res.session_scope() as session:
            events = [id for id, in session.query(Event.id).all()]
        super().__init__(items=events)

    def _getFromFrameId(self, run, camcol, filter, field, which=0):
        """Queries the database for the Event and returns it. In case multiple
        Events correspond to the same frame identifier, supplying  which
        selects one of the returned results.

        The returned Event is expunged from the database session.

        Parameters
        -----------
        run : int
          run identifier
        camcol : int
          camcol identifier
        filter : str
          string identifier
        field : int
          field identifier
        which : int
          if multiple Events are returned, which one in particular is wanted

        """
        with res.session_scope() as session:
            query = session.query(Event).filter(Event.run==run,
                                                Event.filter==filter,
                                                Event.camcol==camcol,
                                                Event.field==field)
            events = query.all()
            if len(events) > 1:
                event = events[which][0]
            elif len(events) == 1:
                event = events[0]
            else:
                return None

            session.expunge(event.frame)
#                session.expunge(event) --> SOMEHOW NOW MAGICALLY CASCADES ON EXPUNGE HAPPEN?!
        return event

    def _getFromItemId(self, eventid):
        """Given an unique Event id queries the database for the row and
        returns it as an appropriate object.
        The returned object is expunged from the database session.

        Parameters
        -----------
        eventid : int
          unique id of the desired Event

        """
        with res.session_scope() as session:
            q = session.query(Event)
            q = q.filter(Event.id==eventid)
            event = q.first()
            if event is not None:
                session.expunge(event.frame)
#                session.expunge(event) --> SOMEHOW NOW MAGICALLY CASCADES ON EXPUNGE HAPPEN?!
        return event

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

        if URI is not None:
            self.initFromDB(URI)

    def initFromDB(self, uri):
        """Connects to a database and indexes all Images therein."""
        imagedb.connect2db(uri)
        with imagedb.session_scope() as session:
            images = [id for id, in session.query(Image.id).all()]
        super().__init__(items=images)

    def _getFromFrameId(self, run, camcol, filter, field, which=0):
        """Queries the database for the Image and returns it. In case multiple
        Imagess correspond to the same frame identifier, supplying  which
        selects one of the returned results.

        The returned Image is expunged from the database session.

        Parameters
        -----------
        run : int
          run identifier
        camcol : int
          camcol identifier
        filter : str
          string identifier
        field : int
          field identifier
        which : int
          if multiple items are returned, which one in particular is wanted

        """
        with imagedb.session_scope() as session:
            query = session.query(Image).filter(Image.run==run,
                                                Image.filter==filter,
                                                Image.camcol==camcol,
                                                Image.field==field)
            images = query.all()
            if len(images) > 1:
                image = images[which][0]
            elif len(images) == 1:
                image = images[0]
            else:
                return None

            session.expunge(image)
        return image

    def _getFromItemId(self, imageid):
        """Given an unique image id queries the database for the row and
        returns it as an appropriate object.
        The returned object is expunged from the database session.

        Parameters
        -----------
        eventid : int
          unique id of the desired Event

        """
        with imagedb.session_scope() as session:
            query = session.query(Image)
            query = query.filter(Image.id==imageid)
            image = query.first()
            if image is not None:
                session.expunge(image)
        return image


    @property
    def image(self):
        """Returns the image pointed to by the current index."""
        return self.item
