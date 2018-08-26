import os as _os

# Make sure these path point to the correct folders
# BOSS       - folder where SDSS data is kept
# SAVE_PATH  - folder where results will be stored
# DEBUG_PATH - folder where images and other debugging files are stored,
#              not mandatory
BOSS = "/home/dino/Desktop/boss"
DEBUG_PATH = _os.path.abspath(_os.curdir)

# Set these paths on your own responsibility
PHOTO_REDUX   = _os.path.join(BOSS, "photo/redux")
BOSS_PHOTOOBJ = _os.path.join(BOSS, "photoObj")

def setup(bosspath=BOSS, debugpath=DEBUG_PATH, photoobjpath=BOSS_PHOTOOBJ,
          photoreduxpath=PHOTO_REDUX):
    global BOSS, DEBUG_PATH, PHOTO_REDUX, BOSS_PHOTOOBJ

    _os.environ["DEBUG_PATH"] = DEBUG_PATH
    _os.environ["BOSS"] = BOSS
    _os.environ["BOSS_PHOTOOBJ"] = BOSS_PHOTOOBJ
    _os.environ["PHOTO_REDUX"] = photoreduxpath

    BOSS = bosspath
    DEBUG_PATH = debugpath
    BOSS_PHOTOOBJ = photoobjpath
    PHOTO_REDUX = photoreduxpath


from .detecttrails import *
from .results import *
#import createjobs
#import gui

#detecttrails: savepath, debugpath, 
