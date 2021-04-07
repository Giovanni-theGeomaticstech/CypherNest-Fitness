from kivymd.app import MDApp
from kivy_garden.mapview import MapSource
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder  # We are going to write .kv builders here
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog  # Dialogue Parameter
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import (
    MDList,
    OneLineAvatarListItem,
    ImageLeftWidget,
)  # Use the MDlist to add the other list items to
from connections import journey_list
from LineClass.line import LineMapLayer
from kivy.utils import platform
from kivymd.uix.label import MDLabel

# Graphs
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib.backend_kivy import FigureCanvas

# Numpy
import numpy as np

from plyer import orientation

journey_toolbar = """
JourneysBoxLayout:
    orientation:'vertical'
    MDToolbar: # Add a Home Icon
        title: 'Journeys'
        left_action_items: [["home", lambda x: app.get_running_app().root.screens[2].return_home(), "Back to Profiles Page"]]
        right_action_items: [["view-list", lambda x: root.show_alert_dialog(), "Back to Journey List"]]
        md_bg_color: .2, .2, .2, 1
        specific_text_color: 1, 1, 1, 1
    MDBottomNavigation:
        panel_color: .2, .2, .2, 1
        specific_text_color: 1, 1, 1, 1
        # pos_hint: {'center_x':0.1}#, 'center_y':0.1}
        
        MDBottomNavigationItem: # The tabs
            id: speed_stats_tab
            name: 'journey_list'
            text: 'Journey List'
            icon: 'map-marker-path'
            specific_text_color: 1, 1, 1, 1
            text_color_active: 1, 0, 1, 1
          
            #Doing the Screen Manager method
            ScreenManager:
                id: Journey-manager
                JourneyListScreen:
                    id:'Journey-lists-screen'
                    name: 'Journey-lists-screen'
                    # ScrollView:
                    MDScrollViewRefreshLayout:
                        id: refresh_view
                        root_layout: self.parent#root
                        refresh_callback: self.parent.refresh_callback
                        JourneyList: # We call our JourneyList class
                            id: journey-list
                            pos_hint: {'center_x':0.1, 'center_y':0.9}
                JourneyMapScreen:
                    name: 'Journey-map-screen'
                    BoxLayout:
                        id: layout-journey
                        orientation: 'vertical'
                        MapView:
                            id: journey-map
        JourneySpeedStats: # The tabs
            id: speed_stats_tab
            name: 'speed_stats'
            text: 'Speed Stats'
            icon: 'speedometer'
            # icon_color: 1, 1, 1, 1
            # text_color_active: 1, 0, 1, 1
            ScrollView:
                id: 'speed_scroll'
                MDBoxLayout:
                    id: 'scroll_box'
                    orientation: 'vertical'
                    spacing: 15
                    MDLabel:
                        text: 'No Journey Selected as yet'
                        size_hint: 0.3,1
                        pos_hint: {"center_x":0.52}
        
        MDBottomNavigationItem: # The tabs
            id: info_stats_tab
            name: 'info_stats'
            text: 'Info Stats'
            icon: 'information'
            # specific_text_color: 1, 1, 1, 1
            # text_color_active: 1, 0, 1, 1
            MDLabel:
                text: 'Coming Soon'
                pos_hint: {"center_x":0.5}
"""

# 1
class JourneysScreen(Screen):
    """Screens For Showing
        - Journey List
        - A Single Journey
        - Speed Stats
        - Basic Journey Stats
    """

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)

        self.name = "Journeys"

        self.bottom_nav = Builder.load_string(journey_toolbar)

        self.add_widget(self.bottom_nav)

    def return_home(self):
        MDApp.get_running_app().root.current = "Profile"

    def review_journeys(self):
        """Update the Journey in the Journey Map Screen"""
        journey_screen_box = self.children[0]
        speed_stats_screen = journey_screen_box.ids["speed_stats_tab"]
        self.graph_schedule = Clock.schedule_once(
            speed_stats_screen.create_figures, 0.5
        )  # Call after 0.5 seconds


# 2
class JourneysBoxLayout(MDBoxLayout):
    """ The Layout Manager for the Journey's Screen"""

    def journey_list_screen(self, menu=None):
        """ Change to Journey list Screen"""
        # print(self.ids) # If you want to see all the id reference
        try:
            journey_manager = self.ids["Journey-manager"]
            journey_manager.current = "Journey-lists-screen"
        except (AttributeError, KeyError):
            print("Cannot Switch")

    def logout(self, menu=None):
        """
            To Logout fully we clear the login token file
            And then chnage to the Login screen
        """
        running_preface = MDApp.get_running_app()

        with open(running_preface.file_path, "w") as f:
            f.write("")  # Empty the User token file
            f.close()
        running_app = MDApp.get_running_app().root
        running_app.current = "Login"

    def show_alert_dialog(self):
        self.journey_list_screen()


# 3
class JourneyListScreen(Screen):
    """The Journey List Screen
            This is where each journey that was created by the user is listed
    """

    def refresh_callback(self, *args):
        """A method that updates the state of your application
        while the spinner remains on the screen."""
        # https://kivymd.readthedocs.io/en/latest/components/refresh-layout/
        def refresh_callback(interval):
            """CLEARS AND UPDATES JOURNEY LISTS"""
            self.refresh_layout = self.children[
                1
            ]  # For the RefreshLayout, index 0 for the Spinner
            self.list_of_journeys = self.refresh_layout.clear_widgets()
            self.refresh_layout.add_widget(JourneyList())
            self.refresh_layout.refresh_done()

        Clock.schedule_once(refresh_callback, 0.8)


# 4
class JourneyList(MDList):
    """
    List of Journeys for the user.
    Note: This Info would come from the Database
    """

    def __init__(self, **kwargs):
        # Here were are going to modify the Drawer List items

        super(MDList, self).__init__(**kwargs)

        self.map_layers = [
            MapSource(
                cache_key="cartodb-darkmatter",
                url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
                attribution="",
            ),
            MapSource(
                cache_key="cartodb-positron",
                url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
                attribution="",
            ),
        ]

        self.journey_feature = None  # Initialize a journey Line
        self.return_btn = None
        self.screen_manager = None
        self.clock = Clock.schedule_interval(
            self.initiate_journeys, 2
        )  # Load the Journey list

    def initiate_journeys(self, instance):
        """ Add our created Journeys"""
        # https://github.com/kivy/plyer/blob/master/plyer/facades/orientation.py
        if platform == "android":
            orientation.set_sensor()
        elif platform == "ios":
            pass

        # Get the current screen
        self.current_screen = self.parent.parent  # Journey-lists-screen

        # Get the Screen Manager
        self.screen_manager = self.current_screen.parent

        # For delayed start up I have to ensure login first
        try:
            running_app = MDApp.get_running_app().root
            if running_app.user_journeys or running_app.user_journeys is None:
                user_id = running_app.user["id"]
                self.user_journeys = journey_list(user_id)
                self.clear_journeys()
                self.list_journeys()
                self.clock.cancel()
        except AttributeError:
            self.user_journeys = {"Place_holder": "Data"}
            print("Journey List not activated")

    def list_journeys(self, unitialized=None):
        """ We add the menu items to area"""
        # We need to attach a name to picked journey
        for index, item in enumerate(self.user_journeys):
            journey_name = f"Journey-{index + 1}"

            # Using a custom Image
            image = ImageLeftWidget(source="img/route_google_map.png")

            # Image right widget is not working in the source code
            item_image = OneLineAvatarListItem(
                text=journey_name, on_press=self.picked_journey
            )
            item_image.journey_info = item  # we add the journey data to the instance
            item_image.add_widget(image)

            self.add_widget(item_image)  # We add it the MDList Class

    def clear_journeys(self):
        """ We clear the Journeys that are added to the screen"""
        self.clear_widgets()

    def picked_journey(self, instance):
        """When the user Chooses a Single Journey"""
        self.journey_popup(instance)  # we pass the name

    def journey_popup(self, instance):
        """ Popup for information in the Journey"""
        journey_name = instance.text
        self.journey_data = instance.journey_info
        popup_info = (
            f"Date Created: {self.journey_data['date_created']} \n"
            f"Journey ID: {self.journey_data['unique_field']} \n"
        )

        # Button to add
        go_to_button = MDFlatButton(
            text="View Journey", on_release=self.journey_dialog_helper
        )  # Button for viewing journey in the map
        close_dialogue = MDFlatButton(text="Close", on_release=self.close_dialog)

        # Dialog Widget

        self.dialog = MDDialog(
            title=instance.text, text=popup_info, buttons=[go_to_button, close_dialogue]
        )
        self.dialog.size_hint = [0.8, 0.8]
        self.dialog.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()  # To close the dialog box

    def journey_dialog_helper(self, obj):
        self.dialog.dismiss()  # To close the dialog box

        # List of all Screens within the Screen Manager
        self.screens_list = self.screen_manager.screens

        # For the Map Screen
        self.map_screen = self.screens_list[1]
        self.journey_layout = self.map_screen.children[0]  # For the Box Layout
        self.mapview = self.journey_layout.children[0]
        self.mapview.map_source = self.map_layers[0]  # Change our Map Layer

        # Change to Journey Map Screen
        self.screen_manager.current = "Journey-map-screen"

        ################################
        # View Journey on Journey Map Screen
        try:
            self.journey_data["feature_info"]["properties"]
        except KeyError:
            self.journey_data["feature_info"]["properties"] = None

        self.view_journey(
            data=self.journey_data["feature_info"]["geometry"]["coordinates"],
            properties=self.journey_data["feature_info"]["properties"],
        )

        # Update Speed stats screen with new journey
        journey_screen = MDApp.get_running_app().root.screens[2]
        journey_screen.review_journeys()

    def view_journey(self, data=None, properties=None):
        """ View Journey shows an individual journey on the map layer
            Parameters:
                data: This a list of coordinates and is used for the initial creation of a new journey
                user_id: This is used to retrieve all the journey's for a user
                journey_id: This is used to choose a journey from all those done by a user
        """
        if data:
            if self.journey_feature == None:  # If it does not exists
                self.journey_feature = (
                    LineMapLayer()
                )  # We initialize a new journey feature
                self.journey_feature.coordinates = data  # A normal List

                # We pass coordinates for the journey feature
                self.journey_feature.name = "Journey Line"
                self.mapview.add_layer(self.journey_feature)
            else:  # Else we just change coordinates
                self.journey_feature.coordinates = data

            # this helps to show the line on the map
            self.mapview.zoom = 14
            self.mapview.center_on(data[0][0], data[0][1])

            # Store Journey Info in the running app
            running_app = MDApp.get_running_app().root

            try:  # Remove this after clearing all other Journeys in Database
                properties["speed"] = np.array(properties["speed"])
                properties["time"] = np.array(properties["time"])
                properties["altitude"] = np.array(properties["altitude"])
                properties["bearing"] = np.array(properties["bearing"])
                MDApp.get_running_app().root.journey_props = properties
                # print("Journey was Chosen")
            except (AttributeError, KeyError, TypeError):
                print("No Journey Chosen As Yet")


class JourneyMapScreen(Screen):
    """Shows a selected journey on the map"""

    pass


class JourneySpeedStats(MDBottomNavigationItem):
    """ This is for the Speed Stats"""

    # Maybe Show all the stats??
    # Or just one
    def __init__(self, **kwargs):
        super(MDBottomNavigationItem, self).__init__(**kwargs)
        self.name = "Speeds Screen"

        # self.graph_schedule = Clock.schedule_interval(self.create_figures, 4)  # Call every 2 seconds

    def create_figures(self, dt):
        running_app = MDApp.get_running_app().root

        scroll_view = self.children[0]
        scroll_view_box = scroll_view.children[0]

        try:
            running_app.journey_props["speed"]
            print("Updating Journey")
            scroll_view_box.clear_widgets()
            self.speed_vs_time_graph()
            self.speed_vs_distance_graph()
            # self.graph_schedule.cancel() # Should update with any new journey
        except AttributeError:
            print("Nothing created exit")

    def speed_vs_time_graph(self):
        """User Travel Speed vs Time"""
        running_app = MDApp.get_running_app().root
        fig, ax = plt.subplots()

        speed = running_app.journey_props["speed"]
        time = running_app.journey_props["time"]

        plt.plot(time, speed)
        plt.title("Speed vs Time Graph")
        plt.xlabel("Time (ms)")
        plt.ylabel("Speed (m/ms)")

        my_graph = FigureCanvas(fig)

        scroll_view = self.children[0]
        scroll_view_box = scroll_view.children[0]
        scroll_view_box.add_widget(my_graph)

    def speed_vs_distance_graph(self):
        """User Travel Speed vs Distance"""
        running_app = MDApp.get_running_app().root
        fig, ax = plt.subplots()

        speed = running_app.journey_props["speed"]
        time = running_app.journey_props["time"]
        distance = (
            speed / time
        )  # Numpy allows us to perform this calc of dividing arrays quickly

        plt.plot(distance, speed)
        plt.title("Speed vs Distance Graph")
        plt.xlabel("Distance (ms)")
        plt.ylabel("Speed (m/ms)")

        my_graph = FigureCanvas(fig)

        scroll_view = self.children[0]
        scroll_view_box = scroll_view.children[0]
        scroll_view_box.add_widget(my_graph)
