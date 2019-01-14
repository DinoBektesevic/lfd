Detection parameters
================================

The detection execution parameters can be viewed/changed by accessing the params
dictionaries of the :class:`~lfd.detecttrails.DetectTrails` class. 

.. code-block:: python
   :linenos:

   import lfd.detecttrails as detect
   foo = detect.DetecTrails(run=2888, camcol=1, filter='i', field=139)
   foo.params_bright
   foo.params_dim
   foo.params_removestars

A special `debug` key can be set to `True` for any of the individual steps of the
algorithm which will produce a very verbose output to stdout as well as save
snapshots of the processed image in intermediate steps to a location pointed to
by `DEBUG_PATH` environmental variable.

.. code-block:: python
   :linenos:

   import lfd.detecttrails as detect
   foo = detect.DetecTrails(run=2888, debug=True)

or, individually

.. code-block:: python
   :linenos:

   foo.params_removestars["debug"] = True
   foo.params_bright["debug"] = True
   foo.params_dim["debug"] = True

The verbose output contains printed statements of acceptance tests such as average
angles, difference in image positions between fitted lines etc. Additionally a
number of images that help identifying the detection limiting factors are saved
as well. For the bright detection step the following images are saved:

* equBRIGHT      - equalized 8bit int image with known objects masked out
* dilateBRIGHT   - equalized and dilated image
* contoursBRIGHT - rectangles that pass the tests are drawn on the image
* boxhoughBRIGHT - rectangles with corresponding fitted lines (set 1)
* equhoughBRIGHT - processed image with second set of fitted lines (set 2)

while the dim detection step in debug mode produces the following set of images:

* equDIM      - equlized, 8bit img, removed objects, increased brightness
* erodedDIM   - equalized and eroded image without known objects
* openedDIM   - equalized, eroded and dilated image without known objects
* contoursDIM - accepted rectangles
* equhoughDIM - processed img with with the first set of fitted lines
* boxhoughDIM - rectangles image with the second set of fitted lines

For the full list of parameters, their types and descriptions see the following
tables sections. To get a better understanding of detection parameters contoursMode,
contoursMethod, minAreaRectMinLen and lwTresh see
:func:`~lfd.detecttrails.processfield.fit_minAreaRect`. For nlinesInSet,
thetaTresh, linesetTresh see :func:`~lfd.detecttrails.processfield.check_theta`.
For removestars params see doc :func:`~lfd.detecttrails.removestars.remove_stars`.

