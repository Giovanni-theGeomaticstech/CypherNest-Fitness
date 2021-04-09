from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder  # We are going to write .kv builders here
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock

# FOR OUR LOCATION BLINKER MARKER
from locationblinker import LocationBlinker

# Plyer package for gps
from plyer import gps

# For our database connection
import json
from connections import journey_post, create_journey_json, retrieve_journey

# from kivy_garden.mapview.geojson import GeoJsonMapLayer
from LineClass.line import LineMapLayer

# Numpy
import numpy as np


# 1
class MapScreen(Screen):
    """ Create Our Map Screen Layout:
        Refer to mapscreen.kv
        - Create our Box Layout (For orientation of objects on screen)
            - Add a Toolbar
            - Add a Map
                - Add Journey upon completion
            - Add the Blinker marker
    """

    def __init__(self, **kwargs):
        """Customizing Screen Initializing"""
        super(Screen, self).__init__(**kwargs)

        self.name = "MapView"

        self.gps_running = False  # Initially have gps off

        self.layout = Builder.load_file("mapscreen.kv")

        self.add_widget(self.layout)

        # Here I added two other map source options
        self.map_layers = {
            "carto-dark": MapSource(
                cache_key="cartodb-darkmatter",
                url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
                attribution="",
            ),
            "carto-white": MapSource(
                cache_key="cartodb-positron",
                url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
                attribution="",
            ),
            # Built In in the Kivy_map package
            "osm": "osm",  # The default
            "osm-hot": "osm-hot",
            "osm-de": "osm-de",  # Dutch OSM
            "osm-fr": "osm-fr",  # French OSM
            "cyclemap": "cyclemap",
            "thunderforest-cycle": "thunderforest-cycle",
            "thunderforest-transport": "thunderforest-transport",
            "thunderforest-landscape": "thunderforest-landscape",
            "thunderforest-outdoors": "thunderforest-outdoors",
        }

        self.new_layer = None

    def change_map(self, instance):
        """ Call this function to change the mapview layer"""
        self.mapview = self.children[0].ids["mapview"]  # Our Map

        if self.mapview.map_source != "osm":
            self.mapview.map_source = self.map_layers["osm"]
        else:
            self.mapview.map_source = self.map_layers["carto-dark"]

    def return_home(self):
        """ Return to profile view """
        if self.mapview:
            self.change_map(instance=None)
        MDApp.get_running_app().root.current = "Profile"

    def start_tracking(self):
        """ Start and stop our GPS Tracking """
        ######################
        # HERE TO CHANGE MAP TILE LAYER
        # I DID NOT TEST IF IT MESSES WITH BLINKER UPDATES BUT I DONT THINK IT SHOULD
        # self.change_map(instance=None) # Change the map type
        ######################

        self.current_screen = MDApp.get_running_app().root.screens[3]  # For this screen
        # Note self is the screen
        self.mapview = self.children[0].ids["mapview"]  # Our Map

        if self.gps_running:  # We stop GPS Tracking
            self.stop_tracking()
            self.gps_running = False
        else:  # We start GPS Tracking
            self.gps_running = True
            GpsActivate().run()

    def stop_tracking(self):
        """ Deactivate GPS Tracking """
        self.gps_blinker = self.children[0].ids["blinker"]  # Our Blinker

        journey_coordinates = (
            self.gps_blinker.stop_blink()
        )  # We get the coordinates of the Journey (Numpy Array)

        # POST OUR JOURNEY TO THE DATABASE
        running_app = MDApp.get_running_app().root
        token = (
            running_app.user_token
        )  # Special User Token/Identification for Authentication

        # Transform an Numpy Array to a normal a list so it can be serialized (JSONified)
        if platform in ["android", "ios"]:
            journey_post(
                data=journey_coordinates.tolist(),
                speed=self.gps_blinker.speed.tolist(),
                time=self.gps_blinker.journey_time.tolist(),
                bearing=self.gps_blinker.bearing.tolist(),
                altitude=self.gps_blinker.altitude.tolist(),
                token=token,
            )
            gps.stop()  # We stop the GPS FROM THE PLYER MODULE

            # View the journey
            self.view_journey(data=journey_coordinates)

    def view_journey(self, data=None):
        """ Display Journey On the Map
            Parameters:
                data: This a list of coordinates and is used for the initial creation of a new journey
        """
        ########################################
        # For the Journey outside
        self.mapview = self.children[0].ids["mapview"]  # Our Map
        self.change_map(instance=None)  # Change the type of map
        ########################################

        if data.any():

            if self.new_layer == None:
                self.new_layer = LineMapLayer()
                self.new_layer.coordinates = data
                self.mapview.add_layer(self.new_layer)
            else:
                self.new_layer.coordinates = data

            self.mapview.zoom = 14

            try:
                center_value = data[1].tolist()
                self.mapview.center_on(
                    center_value[0], center_value[1]
                )  # Idea is to center it on the location of map
            except IndexError:
                center_value = data[0].tolist()


# 2
class GpsActivate:
    """ Activating the GPS"""

    has_centered_map = False  # For Map Center
    time = 0  # For Journey Time
    lat_save = None
    long_save = None

    def run(self):
        """ RUN our GPS """

        self.gps_access_granted = False  # Once the user allows access
        self.gps_blinker = (
            MDApp.get_running_app().root.screens[3].children[0].ids["blinker"]
        )

        # Start blinking the GpsBlinker
        self.gps_blinker.blink()  # The method for this class is where I need to be updating stuff

        if platform == "android":
            from android.permissions import Permission, request_permissions

            # Request permissions on Android to access GPS
            def callback(permission, results):
                """Request Access to Permissions"""
                if all([res for res in results]):
                    from plyer import gps

                    gps.configure(
                        on_location=self.update_blinker_position,
                        on_status=self.on_auth_status,
                    )  # Here we configure auth
                    # We can get speed, lat, long, bearing, altitude
                    # https://github.com/kivy/plyer/blob/master/plyer/facades/gps.py
                    ################################################
                    # FREQUENCY OF GPS CALL
                    # 1000ms minTime = 1 second
                    # minDistance is in Metres
                    gps.start(minTime=1000, minDistance=0)
                    ################################################
                else:
                    print("Did not get all permissions")

            request_permissions(
                [Permission.ACCESS_COARSE_LOCATION, Permission.ACCESS_FINE_LOCATION],
                callback,
            )

        # Configure GPS IOS
        #########################################
        # NOTE I DIDNT GET THE IOS APP WORKING
        if platform == "ios":
            from plyer import gps

            gps.configure(
                on_location=self.update_blinker_position, on_status=self.on_auth_status
            )
            gps.start(minTime=1000, minDistance=0)
        ##########################################

    def update_blinker_position(self, *args, **kwargs):
        """ Updating Blinker Position with the GPS Coordinates """

        my_lat = kwargs["lat"]
        my_lon = kwargs["lon"]
        my_speed = kwargs["speed"]
        my_altitude = kwargs["altitude"]
        my_bearing = kwargs["bearing"]

        if [self.lat_save, self.long_save] != [my_lat, my_lon]:  # if you are moving
            self.lat_save = my_lat
            self.long_save = my_lon

            # Update GpsBlinker position
            self.gps_blinker = (
                MDApp.get_running_app().root.screens[3].children[0].ids["blinker"]
            )  # Attempting to fix position update
            self.gps_blinker.lat = my_lat
            self.gps_blinker.lon = my_lon

            # Label For Testing
            # current_screen = MDApp.get_running_app().root.screens[3]
            # label = current_screen.children[0].ids['temp_speed']
            # label.text = f"Current Speed: {[my_speed]} , Current lat/long: {[my_lat, my_lon]} "

            # We are adding the extra data
            self.gps_blinker.journey_time = np.append(
                self.gps_blinker.journey_time, self.time
            )  # Note time in milliseconds
            self.time += 1
            self.gps_blinker.speed = np.append(self.gps_blinker.speed, my_speed)
            self.gps_blinker.altitude = np.append(
                self.gps_blinker.altitude, my_altitude
            )
            self.gps_blinker.bearing = np.append(self.gps_blinker.bearing, my_bearing)

            # Centering map (**Also ensures that the blinker position updates)
            if not self.has_centered_map:
                map = MDApp.get_running_app().root.screens[3].children[0].ids["mapview"]
                map.center_on(my_lat, my_lon)  # Center Map
                self.has_centered_map = True
            else:
                ###########################################
                # UPDATE MAP CENTERING
                # CURRENTLY EVERY 2 SECONDS
                # CHANGE THIS HERE IF YOU WANT THE BLINKER POSITION TO UPDATE FASTER ON THE MAP
                # 0 MAY NOT WORK , SO DO NOT CHOOSE 0 seconds
                self.center_map_clock = Clock.schedule_once(
                    self.center_map_location, 2
                )  # Center map every 2 seconds
                ###########################################
        else:
            self.time += 1

    def on_auth_status(self, general_status, status_message):
        """ We want to call the popup to check if our GPS has been authorized """
        if general_status == "provider-enabled" or self.gps_access_granted:
            self.gps_access_granted = True
            # pass
        else:
            self.open_gps_access_popup()

    def center_map_location(self, dt):
        """Re-center Map"""
        map = MDApp.get_running_app().root.screens[3].children[0].ids["mapview"]
        map.center_on(self.lat_save, self.long_save)  # Here we center coords

    def open_gps_access_popup(self):
        """ We want to create a popup to say GPS access was not granted """
        close_btn = MDFlatButton(text="Open Profile", on_release=self.close_dialog)
        dialog = MDDialog(
            title="GPS Error",
            text="You need to enable GPS access for the app to function properly",
            buttons=[close_btn],
        )
        self.has_centered_map = False
        dialog.size_hint = [0.8, 0.8]
        dialog.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        dialog.open()

    def close_dialog(self, obj):
        """Close GPS Dialog Error Box"""
        self.dialog.dismiss()  # To close the dialog box
