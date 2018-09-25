# GENERALLY: widths and heights were fixed to the official values and while the
# values of spaces in between the CCD dimensions were availible in the literature
# they did not correspond exactly to calculable quantities - so they have been
# replaced by these new values that seem to match the data better than the
# officially measured (generally) round values.


# width of a camcol, generally corresponds to the width of the image
W_CAMCOL = 2048.0
# with of the space between two camcols, generally corresponds to (W_CAMOL-2*152)
# where the 152 is the overlap in pixels between two adjacent strips as the
# stripe is being imaged. 
W_CAMCOL_SPACING = 1743.820956

# height of a filter, corresponds to the path a single arc on the sky is being
# integrated for. In a single exposure mode this would be the height of the
# image, but because of the drift-scan method the images are artificially cut
# into 1489px heights. True image is cut at 1361px height, 128 of which are
# overlapped with the following image.
H_FILTER = 2048.0
# the space between the two adjacent filters. Not noticeable on the images
# themselves, but if an event occured in the time it took the sky to pass over
# this regioin the event would not be recorded
H_FILTER_SPACING = 660.4435401

# If all camcols and filters and their spaces were added together they would
# demarcate the outer edge of the CCD array where CCD array ends.
MAX_W_CCDARRAY = 21008.0 #unrounded: 21007.10478
MAX_H_CCDARRAY = 12882.0 #unrounded: 12881.77416

# conversion factors between milimeters on the array to arc minutes and pixel
# lengths
ARCMIN2PIX = 0.0066015625
MM2ARCMIN = 3.63535503

