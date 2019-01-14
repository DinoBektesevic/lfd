.. lfd documentation master file, created by
   sphinx-quickstart on Tue Jan  8 13:18:57 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Top level LFD overview
======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   setup
   lfdexamples

Listed below are the packages contained in LFD and a description of their purpose:

* analysis - contains code required to create theoretical cross section profiles
  of defocused meteors and various plotting utilities
* createjobs - contains the code required to create PBS scripts that can be
  submited to a cluster using QSUB commands
* detecttrails - contains the image processing code that detects images containing
  linear features and outputs measured parameters
* errors - (not finished) contains functionality to parse any error messages
  outputed by detecttrails module whilst running on a cluster
* gui - contains the GUI interface to createjobs module and an image browser
  designed for faster and easier verification of results
* results - contains the required functionality to collate and parse the results
  outputed by detecttrails module. 
