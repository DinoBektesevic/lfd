import os.path as path
import glob

import lfd.results as res
from . import imagedb


def frameId2Filename(run, camcol, filter, field, type=".png"):
    """Translates between frame identifiers (run, camcol, filter, field) and
    SDSS style filename of the
        frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}
    format, where type represents the .png, .jpg or other extensions.
    """
    if not all([run, camcol, filter, field]):
        return None
    filename = "frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}"
    filename = filename.format(run=run, camcol=camcol, filter=filter,
                               field=field, type=self.imgtype)
    return os.path.join(self.imgdir, filename)

def filename2frameId(filename):
    """From an SDSS style filename of the
         frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}
    format extracts frame identifiers (run, camcol, filter, field).
    """
    parts = filename.split("-")

    run = int(parts[2])
    camcol = int(parts[3])
    filter = parts[1]
    field = int(parts[-1].split(".")[0])

    return run, camcol, filter, field

def filepath2frameId(filepath):
    """From a filepath to an SDSS styled filename of the
        /path/to/frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}
    extracts frame identifiers (run, camcol, filter, field)
    """
    return filename2frameId(filepath.split("/")[-1])

def eventId2FrameId(eventid):
    """Returns frame identifiers (run, camcol, filter, field) for an Event
    identified by given event id.
    """
    with res.session_scope() as session:
        ev = session.query(res.Event).filter_by(id=eventid).one()
        run, camcol, filter, field = ev.run, ev.camcol, ev.filter, ev.field
    return run, camcol, filter, field

def eventId2Filename(eventid, type=".png"):
    """From an event id constructs a SDSS styled filename."""
    run, camcol, filter, field = self.eventId2FrameId(eventid)
    return self.frameId2Filename(run, camcol, filter, field, type)


def create_imageDB(filenamestr, saveURI, echo=False):
    """Finds all paths to matching files given by filenamestr, extracts their
    frame identifiers and stores them in a database given by saveURI.
    filenamestr can contain wildcards, for example:
        /path/to/dir_containing_subdirs/*/*.png
    will find all /path/to/dir_containing_subdirs/subdir1/frame-r-c-f-f.png
    style filenames.
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





