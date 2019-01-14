Table of dim parameters
=======================

+------------------+----------+-----------------------+------------------------------------+
| Parameter Name   |   Type   | Default value         | Description                        |
+==================+==========+=======================+====================================+
| minFlux          |   float  | 0.02                  | for bright, all negative values are|
|                  |          |                       | set to 0. For dim, all values below|
|                  |          |                       | minFlux treshold are set to zero.  |
+------------------+----------+-----------------------+------------------------------------+
| addFlux          |   float  | 0.5                   | value added to all remaining pixels|
|                  |          |                       | with values still above 0.         |
+------------------+----------+-----------------------+------------------------------------+
| erodeKernel      |  array   | np.ones((3,3))        | Erosion kernel                     |
+------------------+----------+-----------------------+------------------------------------+
| dilateKernel     |  array   | np.ones((9,9))        | Dilation kernel                    |
+------------------+----------+-----------------------+------------------------------------+
| contoursMode     | CV2 const| cv2.RETR_LIST         | All edges returned, see OpenCV     |
|                  |          |                       | of findContours for details.       |
+------------------+----------+-----------------------+------------------------------------+
| contoursMethod   | CV2 const| cv2.CHAIN\_           | All edge points returned, see      |
|                  |          | APPROX_NONE           | OpenCV of findContours             |
+------------------+----------+-----------------------+------------------------------------+
|minAreaRectMinlen | int      | 1                     | Once contours have been found      |
|                  |          |                       | minimal area rectangles are fitted.|
|                  |          |                       | Length of sides are determined. If |
|                  |          |                       | determined. If either side is      |
|                  |          |                       | shorter than this value, in pixels,|
|                  |          |                       | the detection is dismissed.        |
+------------------+----------+-----------------------+------------------------------------+
| lwTresh          | int      | 5                     | ratio that longer/shorter rectangle|
|                  |          |                       | side has to satisfy to be          |
|                  |          |                       | considered a possibly valid        |
|                  |          |                       | detection                          |
+------------------+----------+-----------------------+------------------------------------+
| houghMethod      | int      | 20                    | Min number of votes required in    |
|                  |          |                       | Hough space to be considered a     |
|                  |          |                       | valid line                         |
+------------------+----------+-----------------------+------------------------------------+
| nlinesInSet      | int      | 3                     | Hough transform returns a list of  |
|                  |          |                       | all possible lines. Only           |
|                  |          |                       | nlinesInSet top voted for lines are|
|                  |          |                       | taken into consideration for futher|
|                  |          |                       | checks. This is called a "set" of  |
|                  |          |                       | lines. There are 2 sets in total.  |
+------------------+----------+-----------------------+------------------------------------+
| thetaTresh       | float    | 0.15                  | if within a single set the dispe-  |
|                  |          |                       | rsion of maximal-minimal theta is  |
|                  |          |                       | larger than thetaTresh, detection  |
|                  |          |                       | is dismissed as False. In radians  |
+------------------+----------+-----------------------+------------------------------------+
| linesetTresh     | float    | 0.15                  | if both line sets pass thetaTresh, |
|                  |          |                       | but their respective average thetas|
|                  |          |                       | are larger than this, detection is |
|                  |          |                       | dismissed. In radians.             |
+------------------+----------+-----------------------+------------------------------------+
| dro              | int      | 20                    | if r averages of both Hough line   |
|                  |          |                       | sets are larger than dro then      |
|                  |          |                       | detection is dismissed as false.   |
+------------------+----------+-----------------------+------------------------------------+
| debug            | bool     | False                 | see above.                         |
+------------------+----------+-----------------------+------------------------------------+
