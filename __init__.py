import os as _os

# Make sure these path point to the correct folders
# BOSS       - folder where SDSS data is kept
# SAVE_PATH  - folder where results will be stored
# DEBUG_PATH - folder where images and other debugging files are stored,
#              not mandatory
BOSS = "/home/dino/Desktop/boss"
SAVE_PATH  = _os.path.abspath(_os.curdir)
DEBUG_PATH = _os.path.abspath(_os.curdir)

# Set these paths on your own responsibility
PHOTO_REDUX   = _os.path.join(BOSS, "photo/redux")
BOSS_PHOTOOBJ = _os.path.join(BOSS, "photoObj")

def setup():
    _os.environ["SAVE_PATH"]  = SAVE_PATH
    _os.environ["DEBUG_PATH"] = DEBUG_PATH
    _os.environ["BOSS"] = BOSS
    _os.environ["BOSS_PHOTOOBJ"] = BOSS_PHOTOOBJ


from .detecttrails import *

