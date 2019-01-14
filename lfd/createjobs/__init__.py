"""
Used to create .dqs files necessary to run a job on QSUB system. Main idea was
to create a class that can take care of writing large job(s) without having to
resort to manually editing the templates or produced job script(s) post-fact.
Should alleviate a lot of work and unavoidable confusion, when such jobs are
created manually.

Jobs are created through a Job instance, holding all required parameters. Job
instance uses a writer to populate a template of `*.dqs` scripts that can then
be submitted to the cluster interface.

"""

#PHOTO_REDUX = os.path.join(os.path.expanduser("~"), "Desktop/boss/photo/redux")

def setup(photoreduxpath=None):
    """Sets up the required environmental paths for createjobs module.

    Parameters
    ----------

    photoreduxpath : str
      The path to which PHOTO_REDUX env. var. will be set to. Defaults to
      $BOSS/photoObj

    """
    import os

    if photoreduxpath is None:
        try: bosspath = os.environ["BOSS"]
        except KeyError: bosspath = os.path.join(os.path.expanduser("~"),
                                                 "Desktop/boss")
        photoreduxpath = os.path.join(bosspath, "photo/redux")

    os.environ["PHOTO_REDUX"] = photoreduxpath

from .createjobs import *

