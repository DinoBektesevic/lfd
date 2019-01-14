Examples
========

The setup is mandatory for this package as it needs access to data, so either
set the required environmental variables before running python interpreter or
use one of the provided functions.

If SDSS convention is followed but it is sufficient to point to boss only.

.. code-block:: python
   :linenos:

   import lfd
   lfd.setup_detecttrails()
   lfd.setup_detecttrails("~/path/boss")
   lfd.setup_detecttrails("~/boss", photoreduxpath="/foo/bar")

The above examples are appropriate in the following cases:

* boss directory is located at `~/Desktop/boss` and SDSS conventions apply
* boss directory is not in its default position and SDSS conventions apply
* is a common use case when the run metadata (the .par files) are stored
  elsewhere but image data still follows SDSS convention.

This functionality is replicated in the :func:`lfd.detecttrails.setup` function
but is not as practical as using the :func:`lfd.setup_detecttrails` because it
does not declare default values or assumes SDSS convention. Using either allows
a complete departure from SDSS conventions

.. code-block:: python
   :linenos:

   lfd.detecttrails.setup("~/boss", "~/boss/photoObj", "~/boss/photo/redux")

After that instantiate the `DetectTrails` class, target desired data, and run
:func:`lfd.detecttrails.DetectTrails.process` method. It's practical to import
the module into the namespace. At least 1 data targeting keyword has to be given.

.. code-block:: python
   :linenos:

   import lfd.detecttrails as detect
   foo = detect.DetecTrails(filter="i")
   foo = detect.DetectTrails(camcol=1)
   foo = detect.DetectTrails(run=2888)
   foo = detect.DetectTrails(run=2888, camcol=1)
   foo = detect.DetectTrails(run=2888, camcol=1, filter='i')
   foo = detect.DetectTrails(run=2888, camcol=1, filter='i', field=139)
   foo.process()

The above examples will process different data. Listed in the same order:

* Process filter 'i' of all fields and filters of all runs
* Process camcol 1 of all fields and filters of all runs
* Process all fields, camcols and filters of run 2888
* Process all filters and fields of run 2888 but only for its first camera
  column
* Process only the 'i' filter of camcol 1 of the run 2888 for all fields
* Process this single specific field 

.. caution::

 The size of the selected dataset reduces from top to bottom of the list. The 
 first example (selecting a single filter) will try to process dataset 1/5th the
 size of the entire SDSS dataset!
