from kivy_garden.mapview import MapMarker, MapMarkerPopup
from kivy.animation import Animation
from kivymd.app import MDApp

import numpy as np


class LocationBlinker(MapMarker):
    """KV File Implementation:
        Consult with the locationblinker.kv file.
        KV file <LocationBlinker> builds on our created LocationBlinker class
    """

    # Note time in milliseconds
    journey_time = np.array([])
    speed = np.array([])
    altitude = np.array([])
    bearing = np.array([])

    def blink(self):
        """Activate the blinking animation for the map marker"""
        running_app = MDApp.get_running_app()
        location_coordinates = (
            running_app.curr_journey_points
        )  # Coordinates in the Journey (Numpy array)

        if self.lat and self.lon:
            print(f"Inside Location Blinker: {self.lat}, {self.lon}")
            try:
                if location_coordinates == None:  # If None
                    location_coordinates = np.array([[self.lat, self.lon]])
            except ValueError:
                if (
                    [self.lat, self.lon] != location_coordinates[-1]
                ).all():  # Check that first coordinate does not equal to the previously added
                    location_coordinates = np.concatenate(
                        [location_coordinates, [[self.lat, self.lon]]]
                    )
        running_app.curr_journey_points = location_coordinates

        self.anim = Animation(outer_opacity=0, blink_size=50)  # create animation
        self.active_blink = True  # We need this to let us know of active animation

        # When the animation completes, reset the animation, then repeat
        self.anim.bind(
            on_complete=self.reset
        )  # Bind a function after being on_complete
        self.anim.start(self)  # Starts the animation

    def stop_blink(self):
        """ Stop the Blinking Animation
            return: the array of coordinates
        """
        # Animation
        self.active_blink = False
        self.anim.stop(self)

        # COORDINATES OF THE MARKER/POINT
        running_app = MDApp.get_running_app()
        location_coordinates = running_app.curr_journey_points
        running_app.curr_journey_points = (
            None
        )  # Here we reset journey to be empty Numpy Array

        return location_coordinates

    def reset(self, *args):
        """Reset the Blink to show animation changes. Meaning once we go from:
        default size: 25
        blink size: 50 and opacity:0 -> On complete
        Reset: default size of 25 and opacity of 1
        """
        # Here activate the blink
        if self.active_blink:
            self.outer_opacity = 1
            self.blink_size = self.default_blink_size
            self.blink()  # The function
