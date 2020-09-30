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


    def draw_map(self, last_known):
        """Display basemap with scale, last known xy location, search areas."""

        cv.line(self.img, (20, 370), (70, 370), (0, 0, 0), 2)
        cv.putText(self.img, '0', (8, 370), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv.putText(self.img, '50 Nautical Miles' , (71, 370),
            cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

        # Draw a rectangle for the first search area
        cv.rectangle(self.img, (SA1_CORNERS[0], SA1_CORNERS[1]), (SA1_CORNERS[2], SA1_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '1', (SA1_CORNERS[0] + 3, SA1_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, 0)
        cv.rectangle(self.img, (SA2_CORNERS[0], SA2_CORNERS[1]), (SA2_CORNERS[2], SA2_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '2', (SA2_CORNERS[0] + 3, SA2_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, 0)
        cv.rectangle(self.img, (SA3_CORNERS[0], SA3_CORNERS[1]), (SA3_CORNERS[2], SA3_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '3', (SA3_CORNERS[0] + 3, SA3_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, 0)

        # Post a '+' at the sailor's last known position
        cv.putText(self.img, '+', (last_known), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))

        # Text describing symbols for last known position and actual position if found.
        cv.putText(self.img, '+ = Last Known Position', (274, 355), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv.putText(self.img, '* = Actual Position', (275, 370), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

        # Show the map with Open CV
        cv.imshow('Search Area', self.img)  # map title
        cv.moveWindow('Search Area', 750, 10)  # display the map at the upper left of the monitor
        cv.waitKey(500)  # delay while rendering images to window in milliseconds

    def sailor_final_location(self, num_search_areas):
        """Return the actual x,y location of the missing sailor."""
        # Find sailor coordinates with respect to any Search Area sub-array.
        # The coordinates generated by random.choice() will range from 0 to 49.
        self.sailor_actual[0] = np.random.choice(self.sa1.shape[1], 1)
        self.sailor_actual[1] = np.random.choice(self.sa2.shape[0], 1)
        #print(np.shape(self.SA1))

        # Pick a search area with the random module to us ethe above coordinates with the full base map image.
        area = int(random.triangular(1, num_search_areas + 1))

        if area == 1:
            x = self.sailor_actual[0] + SA1_CORNERS[0]
            y = self.sailor_actual[1] + SA2_CORNERS[1]

            # Keep track of the search area by updating self.area_actual attribute
            self.area_actual = 1

        elif area == 2:
            x = self.sailor_actual[0] + SA2_CORNERS[0]
            y = self.sailor_actual[1] + SA2_CORNERS[1]
            self.area_actual = 2

        elif area == 3:
            x = self.sailor_actual[0] + SA3_CORNERS[0]
            y = self.sailor_actual[1] + SA3_CORNERS[1]
            self.area_actual = 3

        return x, y

    def calc_search_effectiveness(self):
        """Set decimal search effectiveness value per search area."""

        self.sep1 = random.uniform(0.2, 0.9)
        self.sep2 = random.uniform(0.2, 0.9)
        self.sep3 = random.uniform(0.2, 0.9)

    def conduct_search(self, area_num, area_array, effectiveness_prob):
        """Return search results and list of searched coordinates."""

        # Generate a list of all the coordinates within a given search area
        local_y_range = range(area_array.shape[0])
        local_x_range = range(area_array.shape[1])

        # Generate the list of all coordinates in the search area, use the itertools
        coords = list(itertools.product(local_x_range, local_y_range))
        # Shuffle the list of coordinates so you won’t keep searching the same
        random.shuffle(coords)
        # Use index slicing to trim the list based on the search effectiveness probability.
        coords = coords[:int((len(coords) * effectiveness_prob))]

        # Assign a local variable to hold the sailor’s actual location
        loc_actual = (self.sailor_actual[0], self.sailor_actual[1])

        # Use a conditional to check that the sailor has been found
        if area_num == self.area_actual and loc_actual in coords:
            return f'Found in Area{area_num}', coords
        else:
            return 'Not Found', coords

    def revise_target_probs(self):
        """Update area target probabilities based on search effectiveness."""
        denom = self.p1 * (1 - self.sep1) + self.p2 * (1 - self.sep2) \
                + self.p3 * (1 - self.sep3)

        self.p1 = self.p1 * (1 - self.sep1) / denom
        self.p2 = self.p2 * (1 - self.sep2) / denom
        self.p3 = self.p3 * (1 - self.sep3) / denom

def draw_menu(search_num):
    """Print menu of choices for conducting area searches."""
    print(f'\nSearch{search_num}')
    print(
        """
        Choose next areas to search:
        0 - Quit
        1 - Search Area 1 twice
        2 - Search Area 2 twice
        3 - Search Area 3 twice
        4 - Search Areas 1 & 2
        5 - Search Areas 1 & 3
        6 - Search Areas 2 & 3
        7 - Start Over
        """
    )

def main():
    '''Runs the program above'''

    # Creates the game application using the Search class
    app = Search('Cape Python')
    app.draw_map(last_known=(160, 290)) # Last known x,y position of sailor
    sailor_x, sailor_y = app.sailor_final_location(num_search_areas=3)
    print('-' * 65)
    print("\nInitial Target (p) Probabilities: ")
    print(f"P1 = {app.p1:.3f}, P2 = {app.p2:.3f}, P3 = {app.p3:.3f}")
    search_num = 1 # Keeps track of the number of searches

    # Loop runs until user chooses to exit
    while True:
        app.calc_search_effectiveness()  # Calculate search effectiveness
        draw_menu(search_num)  # Displays menu and accepts the search number
        choice = input("Choice: ") # Accept user input

        if choice == "0":
            sys.exit()

        elif choice == "1":
            # Generate 2 sets of results and coordinates
            results_1, coords_1 = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2 = app.conduct_search(1, app.sa1, app.sep1)
            # Add the two lists above toghether and remove duplicates, divide the pixels in the search area by the set
            app.sep1 = (len(set(coords_1 + coords_2))) / (len(app.sa1) ** 2)
            app.sep2 = 0
            app.sep3 = 0

        elif choice == "2":
            results_1, coords_1 = app.conduct_search(2, app.sa2, app.sep2)
            results_2, coords_2 = app.conduct_search(2, app.sa2, app.sep2)
            app.sep1 = 0
            app.sep2 = (len(set(coords_1 + coords_2))) / (len(app.sa2) ** 2)
            app.sep3 = 0

        elif choice == "3":
            results_1, coords_1 = app.conduct_search(3, app.sa3, app.sep3)
            results_2, coords_2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = 0
            app.sep2 = 0
            app.sep3 = (len(set(coords_1 + coords_2))) / (len(app.sa3) ** 2)

        #  divide teams between two areas. In this case, there’s no need to recalculate the SEP.
        elif choice == "4":
            results_1, coords_1 = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2 = app.conduct_search(2, app.sa2, app.sep2)
            app.sep3 = 0

        elif choice == "5":
            results_1, coords_1 = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep2 = 0

        elif choice == "6":
            results_1, coords_1 = app.conduct_search(2, app.sa2, app.sep2)
            results_2, coords_2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = 0

        # If the player finds the sailor and wants to play again or just wants to restart, call the main() function
        elif choice == "7":
            main()

        else:
            print("\nSorry, but that isn't a valid choice.", file=sys.stderr)
            continue


        app.revise_target_probs() # Use Bayes' rule to update target probs.

        print(f"\nSearch {search_num} Results 1 = {results_1}", file=sys.stderr)
        print(f"\nSearch {search_num} Results 2 = {results_2}", file=sys.stderr)
        print(f"Search {search_num} Effectiveness (E):")
        print(f"E1 = {app.sep1:.3f}, E2 = {app.sep2:.3f}, E3 = {app.sep3:.3f}")

        if results_1 == 'Not found' and results_2 == 'Not Found':
            print(f"\nNew Target Probabilities (P) for Search {search_num + 1}:")
            print(f"P1 = {app.p1:.3f}, P2 = {app.p2:.3f}, P3 = {app.p3:.3f}")

        else:
            cv.circle(app.img, (sailor_x, sailor_y), 3, (255, 0,0), -1)
            cv.imshow('Search Area', app.img)
            cv.waitKey(1500)
            main()
        search_num += 1

    if __name__ == '__main__':
        main()































