from kivymd.app import MDApp
from kivy.lang import Builder  # We are going to write .kv builders here
from kivymd.uix.button import MDRoundFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog  # Dialogue Parameter

# The different Screen imports
# https://kivy.org/doc/stable/api-kivy.uix.screenmanager.html

from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen, Screen

# Screens
from profile_screen import ProfileScreen
from login_screen import LoginScreen
from journeys_screen import JourneysScreen
from map_screen import MapScreen
from other_users_screen import OtherUsersScreen
from registration_screen import RegisterScreen

import numpy as np

# # OS Imports
import os



# App Lifecycle
# https://kivy.org/doc/stable/guide/basic.html

# Screen Manager Settings
# https://kivy.org/doc/stable/api-kivy.uix.screenmanager.html

# Available Theme colours for icons/widgets in our application
theme_colours = np.array([
    "Red",
    "Pink",
    "Purple",
    "DeepPurple",
    "Indigo",
    "Blue",
    "LightBlue",
    "Cyan",
    "Teal",
    "Green",
    "LightGreen",
    "Lime",
    "Yellow",
    "Amber",
    "Orange",
    "DeepOrange",
    "Brown",
    "Gray",
    "BlueGray",
])

# All Components
# https://kivymd.readthedocs.io/en/latest/components/toolbar/index.html


class MainApp(MDApp):

    """ This is the main Application area
    The Structure:

    Check build in methods for an App Class

    1. We Want to set our Application theme
    2. We want activate features on application Start

    Main Screens:
        - Login
        - Registration
        - Profile Screen
        - Journey List Screen (All the journeys for a user)
        - Map Screen (Creating a new Journey)
        - Other Users Screen (Show Information for Other Users)
    """
    path = "cache"
    filename = "user_token.txt"

    def build(self):
        """This Builds our Application"""

        self.sm = ScreenManager() # Here we build screen Manager
    
        return self.sm

    def on_start(self):
        """Upon Application Start up:
            1. Change our colour theme
            2. Read token from or Create a file for token storage
            3. Add our Screens 
        """

        # Define our application theme
        # Choosable theme colours from ThemeManager

        self.theme_cls.primary_palette = theme_colours[
            3
        ]

        ##############################################################
        # Creating / Accessing User token from File for cached login
        cache_folder = os.path.join(self.user_data_dir, self.path)
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
            self.file_path = os.path.join(cache_folder, self.filename)
        
        self.file_path = os.path.join(cache_folder, self.filename)

        try:
            with open(self.file_path, 'r') as f:
                self.user_file_token = f.read() # Make this accessible to login page
                f.close()
                # print(self.user_file_token)
        except (AttributeError, FileNotFoundError): # Create If File not found
            with open(self.file_path, "w") as f:
                # f.write('')
                self.user_file_token = ''
                f.close()
        ################################################################


        # Profile Screen (1)
        self.profile_screen = ProfileScreen()
        self.sm.add_widget(self.profile_screen)  # Add it to the screen manager
         # Login Screen (2)
        self.login_screen = LoginScreen()
        self.sm.add_widget(self.login_screen)  # Add it to the screen manager

        # Journey List Screen (3)
        self.journeys_screen = JourneysScreen()
        self.sm.add_widget(self.journeys_screen)  # Add it to the screen manager

        # Map Screen (4)
        self.map_screen = MapScreen()
        self.sm.add_widget(self.map_screen)

        # Numpy is alot faster and takes up significantly less memory than our normal python Lists
        # Especially with larger arrays (for eg. imagine creating arrays from a range of numbers up to 100000000)
        # The normal lists takes 71.5 seconds while numpy took 6.1 seconds thus 11 times faster
        # This is important for when we are moving around and changing our coordinates
        # self.curr_journey_points = np.array([]) # We initialize this at the start of our application to store coordinates
        self.curr_journey_points = None # We initialize this at the start of our application to store coordinates

        # Other Users Screen (5)
        self.other_users_screen = OtherUsersScreen()
        self.sm.add_widget(self.other_users_screen)

        # Registration Screen (6)
        self.registration_screen = RegisterScreen()
        self.sm.add_widget(self.registration_screen)

        self.sm.current = "Login"  # Start up Screen

if __name__ == "__main__":
    """Run our App"""
    app = MainApp()
    app.run()
