"""ImageChecker is a image browser designed to speed up results verification.

After processing large ammount of data, depending on the selected detection
parameters, there would be none to a lot of false positive detections in the
dataset. These potential detections would need to be manually checked in some
situations to ensure the quality of the results.

The frames of interest, i.e. the results or its subset, would be converted,
keeping in mind to scale and preprocess the images appropriately for their
intended use, to one of the supported formats (png, jpeg, gif, ppm/pgm) and
their frame identifiers and paths stored in a database. ImageCheker would
connect to the results and images database and would be able to browse through
keyed either on the images, or detected events.

While this is possible to do on the cluster itself, using X forwarding, it is
not recomended due to large potential latency and possibly long image download
times. For fastest possible verification it is best to run ImageChecker
locally. ImageChecker was designed to facilitate fast verification and
correction of results and was not intended to be, yet another, FITS viewer.
"""
from lfd.gui.imagechecker import imagechecker
