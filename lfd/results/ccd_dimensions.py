"""This module contains all neccessary constants to define a usable coordinate
system on, and between, the images::

      1            2             3            4            5          6 CAMCOLS
  -------------------------------------------------------------------------...>
  |x---------   x---------   x---------   x---------   x---------   x---------
  ||        |   |        |*P1|        |   |        |   |        |   |        |
 r||  CCD   |   |  CCD   | \ |  CCD   |   |  CCD   |   |  CCD   |   |  CCD   |
  ||        |   |        |  \|        |   |        |   |        |   |        |
  |----------   ----------   \---------   ---------- __----------   ----------
  |                           \-->lin. feat           ^ H_FILTER_SPACING
  |x---------   x---------   x-\--------   x---------_|_ 
  ||        |   |        |   |  \      |   |        | ^
 i||  CCD   |   |  CCD   |   |   * P2  |   |  CCD   | | H_FILTER
  ||        |   |        |   |         |   |        | |
  |----------   ----------   -----------   ----------_|_
 u||<------>|<->|
  | W_CAMCOL  W_CAMCOL_SPACING
  .
  .
  . FILTERS (riuzg)
  ˘

Widths and heights were fixed to the official values and while the values of
spaces in between the CCD dimensions were availible in the literature they did
not correspond exactly to calculable quantities - so they have been replaced by
these new values that seem to match the data better than the ones provided in
literature.

CONSTANTS
---------

W_CAMCOL : float
  2048, the width of one CCD, in pixels, corresponds to image width
H_FILTER : float
  2048, the height one one CCD, in pixels, images are cut to 1489px height with
  139px of overlap between them, there are usually 3 images in a CCD at a given
  time, although only 2 is also possible.
W_CAMCOL_SPACING : float
  1743.820956, the width the gap beween two camera columns
H_FILTER_SPACING : float
  660.4435401, the spacing between two rows of filters, these gaps can not be
  noticed on the images but it takes some time for the sky to drift through
  them.
MAX_W_CCDARRAY : float
  21008.0, unrounded: 21007.10478, the lower edge of the CCD array, in pixels,
  if all W_CAMCOL and W_CAMCOL_SPACINGS were added together
MAX_H_CCDARRAY :
  12882.0, unrounded: 12881.77416, the lower edge of the CCD array, in pixels,
  if all H_FILTER and H_FILTER_SPACINGS were added together
ARCMIN2PIX : float
  0.0066015625, arcminutes/pixel, pixel scale, corresponds to0.396 arcsec/pixel
  , but expressed in minutes because of how values were given in the tables.
MM2ARCMIN : float
  3.63535503, detector image scale, mm/arcminute.
"""

W_CAMCOL = 2048.0
W_CAMCOL_SPACING = 1743.820956

H_FILTER = 2048.0
H_FILTER_SPACING = 660.4435401

MAX_W_CCDARRAY = 21008.0 #unrounded: 21007.10478
MAX_H_CCDARRAY = 12882.0 #unrounded: 12881.77416

ARCMIN2PIX = 0.0066015625
MM2ARCMIN = 3.63535503

