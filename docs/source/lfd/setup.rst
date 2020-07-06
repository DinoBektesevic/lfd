Setup
=====

Certain modules depend on certain environmental variables to figure out where the
data lives and how it's organized. It is recommended that conventional SDSS file
naming and directory structures are followed. SDSS generally follows structure
shown below:

|  boss
|  ├ photo
|  │ └── redux
|  │     ├── photoRunAll-dr{DR}.par
|  │     └── runList.par
|  └ photoObj
|    ├── 301
|    │   └── [RUN]
|    │       └── [CAMCOL]
|    │           └── photoObj-{PADDED_RUN}-CAMCOL-{PADDED_FIELD}.fits 
|    └── frames
|        └── [RUN]
|            └── [CAMCOL]
|                └── frame-{FILTER}-{PADDED_RUN}-CAMCOL-{PADDED_FIELD}.fits


Where the `RUN` marks the integer designation of the desired run (i.e. 94, 2888)
and `PADDED_RUN` marks the integer run designation padded to 6 digits by
preceding zeros (i.e. 000094, 002888). The slight difference between the
`PADDED_RUN` and `PADDED_FIELD` is the fact that the field is only padded to 4
digits  The square bracketted items (i.e. `[RUN]` means a directory named 94 or
2888). Finally there are two files requried to detect linear features. One is the
image itself - these are the `frame` files (i.e. frame-i-000094-1-0168.fits) and
the other required file is the catalog of all detected sources on that image -
these are the `photoObj` files.

The files `photoRunAll-dr{DR}.par` and `runList.par` store the parameters of all
the runs that SDSS made up to the DR (Data Release number). This is determined by
the Data Release number from which the data was selected and downloaded from -
f.e. for DR10 data release the appropriate file is `photoRunAll-dr10.par`. These
files are downloadable from the SDSS servers.

The SDSS directory structure can be overriden by providing the required
environmental variables. The environmental variables point to different folders
and subfolders of this structure. They are listed and explained in the following
table:

+----------------+------------------------------+
| Env. Var. Name | Points to                    |
+================+==============================+
| BOSS           | Top level `boss` directory   |
+----------------+------------------------------+
| PHOTO_OBJ      | `boss/photoObj` directory    |
+----------------+------------------------------+
| PHOTO_REDUX    | `boss/photo/redux` directory |
+----------------+------------------------------+

These variables can be set through the terminal prior, or after, importing the
`lfd` library by using the following commands::

 export $ENVVAR=/some/path

or::

 setenv $ENVVAR=/some/path

depending on the shell and OS used. Or they can be set by using top-level
functionality in the `lfd` module.
 
.. autofunction:: lfd.setup_detecttrails

.. autofunction:: lfd.setup_createjobs
   :noindex:
