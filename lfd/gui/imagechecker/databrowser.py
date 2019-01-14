"""Data Browsers are classes that maintain index consistency between two
Indexers and provide the functionality required to browse two indexers
simultaneously. Since the source databases for results and images could be
completely disjointed this means one of the Indexers is designated as a primary
indexer. Browsing follows primary indexer while the secondary indexer is
queried for the corresponding item.

"""
import os

from lfd.gui.imagechecker.indexers import ImageIndexer, EventIndexer
from lfd.gui.imagechecker.imagedb import session_scope

class GenericBrowser(type):
    """GenericBrowser metaclass offers the ability to rename the values of
    attributes being browsed through into something more appropriate. In the
    case of an EventBrowser for example that would be::

      primary --> Event
      secondary --> Images

    and the other way around for ImageBrowser. This is completely superfluous
    and here more because I wanted to tr something out than out of any real
    neccessity.

    """
    def __new__(cls, name, bases, attrs):
        if len(bases) > 0 and "rename" in attrs.keys():
            for old, new in attrs["rename"].items():
                attrs[new] = bases[0].__dict__[old]
        return super(GenericBrowser, cls).__new__(cls, name, bases, attrs)

class Browser(metaclass=GenericBrowser):
    """Browser is the generic abstraction of a browser that iterates over the
    pairs of (primary, secondary) items. Given objects capable of itemizing,
    i.e. indexing, the primary and secondary items Browser will ensure the
    consistency of the browsing index between the two indexers. For example, if
    we wanted to browse to the next value of primary indexer the following
    actions are performed:

     1) invokes the next method of the primary indexer
     2) identifies that item
     3) invokes the get method of the secondary indexer.

    This is neccessary since the sets of items indexed by primary and secondary
    can be completely disjoint.

    The attributes and methods of this class are mainly private or hidden. By
    inheriting this class and declaring a dictionary class attribute "rename"
    on that class it is possible to rename the methods of this class into
    something more appropriate such as assigning the name 'images' to
    '_primary' when dealing with ImageBrowser class etc.

    Parameters
    ----------
    primaryIndexer : lfd.gui.imagechecker.Indexer
      the primary Indexer (EventIndexer or ImageIndexer)
    secondaryIndexer : lfd.gui.imagechecker.Indexer
      the secondary Indexer

    """
    def __init__(self, primaryIndexer=None, secondaryIndexer=None):
        """Identify primary and secondary indexer classes. To instantiate the
        actual indexers one of the _initPrimary or _initSecondary methods has
        to be called.

        """
        self.primaryIndexer = None if primaryIndexer is None else primaryIndexer
        self.secondaryIndexer = None if secondaryIndexer is None else secondaryIndexer
        self.__primary = None
        self.__secondary = None

    def _initPrimary(self, URI):
        """Instantiate the primary indexer."""
        self.__primary = self.primaryIndexer(URI)
        run    = self.__primary.item.run
        camcol = self.__primary.item.camcol
        filter = self.__primary.item.filter
        field  = self.__primary.item.field
        if self.__secondary is not None:
            self.__secondary.get(run, camcol, filter, field)

    def _initSecondary(self, URI):
        """Instantiate the secondary indexer."""
        self.__secondary = self.secondaryIndexer(URI)
        run    = self.__primary.item.run
        camcol = self.__primary.item.camcol
        filter = self.__primary.item.filter
        field  = self.__primary.item.field
        self.__secondary.get(run, camcol, filter, field)

    def getNext(self):
        """Advance the index of the primary by a step and then find if the
        secondary contains the newly selected object.

        """
        if self.__primary is not None:
            self.__primary.next()
            tmp = self._primary.item #images.image
            self.__secondary.get(run=tmp.run, camcol=tmp.camcol, filter=tmp.filter,
                               field=tmp.field)
    def getPrevious(self):
        """Regress the index of the primary by a step and then find if the
        secondary contains the newly selected object.

        """
        if self.__primary is not None:
            self.__primary.previous()
            tmp = self._primary.item
            self.__secondary.get(run=tmp.run, camcol=tmp.camcol, filter=tmp.filter,
                                 field=tmp.field)

    def get(self, run, camcol, filter, field, which=0):
        """Given frame specifiers (run, camcol, filter, field) select and
        advance both indexers to the item if possible. Relationship from
        primary to secondary indexer can be many to one, so providing 'which'
        allows selection on a particular secondary of interest.

        """
        self.__primary.get(run=run, camcol=camcol, filter=filter, field=field,
                        which=which)
        self.__secondary.get(run=run, camcol=camcol, filter=filter, field=field)

    @property
    def _primary(self):
        """The items indexed by the primary indexer."""
        return self.__primary

    @property
    def _secondary(self):
        """The items indexed by the secondary indexer."""
        return self.__secondary

    @property
    def _pitem(self):
        """The item, of the primary indexer, pointed to by the current index."""
        return self.__primary.item

    @property
    def _sitem(self):
        """The item, of the secondary indexer, pointed to by the current index."""
        return self.__secondary.item


class EventBrowser(Browser):
    """A Browser which primary set of items to browse through are Events. For
    each Event indexed it will attempt to find a corresponding image. This
    Browser guarantees that all Events will be Browsed, but not all indexed
    images will be browsed through.

    Parameters
    ----------
    resdbURI : str
      URI of the database of Events (i.e. results)
    imgdbURI : str
      URI of the database of Images

    """
    rename = {"_primary":"events", "_secondary":"images", "_pitem":"event",
              "_sitem":"image", "_initPrimary":"initEvents",
              "_initSecondary":"initImages"}

    def __init__(self, resdbURI=None, imgdbURI=None):
        super().__init__(primaryIndexer=EventIndexer,
                         secondaryIndexer=ImageIndexer)

        if resdbURI is not None:
            self.initEvents(resdbURI)

        if imgdbURI is not None:
            self.initImages(imgdbURI)


class ImageBrowser(Browser):
    """A Browser which primary set of items to browse through are Images. For
    each Image indexed it will attempt to find a corresponding Event. This
    Browser guarantees that all Images will be browsed, but not all indexed
    events will be browsed through.

    Parameters
    ----------
    resdbURI : str
      URI of the database of Events (i.e. results)
    imgdbURI : str
      URI of the database of Images

    """
    rename = {"_primary":"images", "_secondary":"events", "_pitem":"image",
              "_sitem":"event", "_initPrimary":"initImages",
              "_initSecondary":"initEvents"}

    def __init__(self, resdbURI=None, imgdbURI=None):
        super().__init__(primaryIndexer=ImageIndexer,
                         secondaryIndexer=EventIndexer)

        if imgdbURI is not None:
            self.initImages(imgdbURI)

        if resdbURI is not None:
            self.initEvents(resdbURI)
