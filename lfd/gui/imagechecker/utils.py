import os.path as path
import glob

import lfd.results as res
from lfd.gui.imagechecker import imagedb


def frameId2Filename(run, camcol, filter, field, type=".png"):
    """Translates between frame identifiers and  SDSS style filename of the::

        frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}

    format, where type represents the .png, .jpg or other extensions.

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
    type : str
      file extension (.png, .jpeg etc...)

    """
    if not all([run, camcol, filter, field]):
        return None
    filename = "frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}"
    filename = filename.format(run=run, camcol=camcol, filter=filter,
                               field=field, type=self.imgtype)
    return os.path.join(self.imgdir, filename)

def filename2frameId(filename):
    """From an SDSS style filename of the::

         frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}

    format extracts frame identifiers (run, camcol, filter, field).


    Parameters
    -----------
    filename : str
      just the filename, no prepended path

    """
    parts = filename.split("-")

    run = int(parts[2])
    camcol = int(parts[3])
    filter = parts[1]
    field = int(parts[-1].split(".")[0])

    return run, camcol, filter, field

def filepath2frameId(filepath):
    """From a filepath extracts SDSS frame identifiers. Filepath must be of the
    followng format::

        /path/to/frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}


    Parameters
    -----------
    filepath : str
      path-like string
    """
    return filename2frameId(filepath.split("/")[-1])

def eventId2FrameId(eventid):
    """Returns frame identifiers (run, camcol, filter, field) for an Event
    identified by given event id.


    Parameters
    -----------
    eventid : int
      unique Event identifier

    """
    with res.session_scope() as session:
        ev = session.query(res.Event).filter_by(id=eventid).one()
        run, camcol, filter, field = ev.run, ev.camcol, ev.filter, ev.field
    return run, camcol, filter, field

def eventId2Filename(eventid, type=".png"):
    """From an event id constructs a SDSS styled filename via frameId2Filename
    function.

    Parameters
    -----------
    eventid : int
      unique Event identifier
    type : str
      file extension (.png, .jpeg etc...)
      
    """
    run, camcol, filter, field = self.eventId2FrameId(eventid)
    return self.frameId2Filename(run, camcol, filter, field, type)


def create_imageDB(filenamestr, saveURI, echo=False):
    """Finds all paths to matching files given by filenamestr, extracts their
    frame identifiers and stores them in a database given by saveURI. 

    Examples
    --------
    Filenamestr can contain wildcards, f.e.:

    >>> create_imageDB("/path/to/dir_containing_subdirs/*/*.png",
        "sqlite:///foo.db")

    will find all /path/to/dir/subdirs/frame-run-camcol-filter-frame.png styled
    filenames and add their frame identifiers and paths to foo DB.

    Parameters
    -----------
    filenamestr : str
      wildcarded string that will be used to match all desired image files
    saveURI : str
      URI containing type and location of the images database

    """
    imagedb.connect2db(saveURI, echo)
    files = glob.glob(rootdir)
    images = []

    for filepath in files:
        run, camcol, filter, field = filepath2frameId(filepath)
        images.append(imagedb.Image(run, camcol, filter, field, filepath))

    with imagedb.session_scope() as session:
        session.add_all(images)
        session.commit()





