Table of removestars parameters
===============================

+------------------+----------+-----------------------+------------------------------------+
| Parameter Name   |   Type   | Default value         | Description                        |
+==================+==========+=======================+====================================+
| pixscale         |  float   | 0.396                 | SDSS pixel scale in arcsec/pixel.  |
+------------------+----------+-----------------------+------------------------------------+
| defaultxy        | int      | 20                    | Half of the length of squares drawn|
|                  |          |                       | over stars. Used when there's no   |
|                  |          |                       | Petrosian radius availible or if   |
|                  |          |                       | length/2 of square sides are larger|
|                  |          |                       | than maxxy. In pixels.             |
+------------------+----------+-----------------------+------------------------------------+
| maxxy            | int      | 60                    | Max allowed half-length of square  |
|                  |          |                       | sides. Max covered area is 120x120 |
+------------------+----------+-----------------------+------------------------------------+
| filter_caps      | dict     | {u:22., g:22.2,       | Objects dimmer than filter_caps    |
|                  |          |  r:22.2, i:21.3,      | will not be removed (filter        |
|                  |          |  z:20.5}              | dependent)                         |
+------------------+----------+-----------------------+------------------------------------+
| magcount         | int      | 3                     | max allowed number of filters in   |
|                  |          |                       | which magnitude difference is      |
|                  |          |                       | larger than maxmagdiff             |
+------------------+----------+-----------------------+------------------------------------+
| maxmagdiff       | float    | 3                     | Min number of votes required in    |
|                  |          |                       | Hough space to be considered a     |
|                  |          |                       | valid line                         |
+------------------+----------+-----------------------+------------------------------------+
| debug            | bool     | False                 | see above.                         |
+------------------+----------+-----------------------+------------------------------------+
