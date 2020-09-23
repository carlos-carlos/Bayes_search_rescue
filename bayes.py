import sys
import random
import itertools

import numpy as np
import cv2 as cv

'''
simulates the search for a missing sailor over three contiguous search areas. 
display a map, print a menu of search choices for the user, randomly choose a location for the sailor, 
and either reveal the location if a search locates him 
or do a Bayesian update of the probabilities of finding the sailor for each search area.
'''

MAP_FILE = 'cape_python.png'

SA1_CORNERS = (130, 265, 180, 315) # (UL-X, UL-Y, LR-X, LR-Y)
SA2_CORNERS = (80, 255, 130, 305) # (UL-X, UL-Y, LR-X, LR-Y)
SA3_CORNERS = (105, 205, 155, 255) # (UL-X, UL-Y, LR-X, LR-Y)

class Search():
    """Bayesian Search & Rescue game with 3 search areas."""

    def __init__(self, name):
        self.name = name
        self.img = cv.imread(MAP_FILE, cv.IMREAD_COLOR)

        # check the map file is present
        if self.img is None:
            print(f'Could not load map file {MAP_FILE}',
                  file=sys.stderr)
            sys.exit(1)

        # When the sailor is found. area_actual = search are. sailor_actual = coordinates in the area
        self.area_actual = 0
        self.sailor_actual = [0, 0] # As "local" coordinates within search area

        # Local coordinates within the search areas from 'y' to 'x' upper-left to lower-right
        self.sa1 = self.img[SA1_CORNERS[1] : SA1_CORNERS[3],
                            SA1_CORNERS[0] : SA1_CORNERS[2]]

        self.sa2 = self.img[SA2_CORNERS[1] : SA2_CORNERS[3],
                            SA2_CORNERS[0] : SA2_CORNERS[2]]

        self.sa3 = self.img[SA3_CORNERS[1] : SA3_CORNERS[3],
                            SA3_CORNERS[0] : SA3_CORNERS[2]]

        # Probability of finding the sailor for each area
        self.p1 = 0.2
        self.p2 = 0.5
        self.p3 = 0.3

        # SEP attributes
        self.sep1 = 0
        self.sep2 = 0
        self.sep3 = 0

