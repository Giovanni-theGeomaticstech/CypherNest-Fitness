from kivymd.app import MDApp
from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder  # We are going to write .kv builders here
from kivymd.uix.button import MDRoundFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog  # Dialogue Parameter
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

from kivymd.uix.list import (
    OneLineListItem,
    MDList,
    IconLeftWidget,
    ImageRightWidget,
    OneLineIconListItem,
    OneLineAvatarListItem,
    ImageLeftWidget,
)  # Use the MDlist to add the other list items to
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *


from connections import user_list
from map_screen import MapScreen
from LineClass.line import LineMapLayer

# Graphs
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from kivy.garden.matplotlib.backend_kivy import FigureCanvas

users_toolbar = """
UserBoxLayout:
    spacing:15
    orientation:'vertical'
    MDToolbar: # Add a Home Icon
        id:user_bar
        title: 'Users List'
        left_action_items: [["home", lambda x: app.get_running_app().root.screens[2].return_home(), "Back to Profiles Page"]] # 2 is this screen
        # right_action_items: [["home", lambda x: app.get_running_app().root.screens[2].return_journeys_list(), "Back to Profiles Page"]]
        md_bg_color: .2, .2, .2, 1
        specific_text_color: 1, 1, 1, 1
    MDScrollViewRefreshLayout:
        id:refresh_bar
        root_layout: self.parent#root
        refresh_callback: self.parent.refresh_callback
        UsersList: # We call our UsersList class
            id: users-list
            pos_hint: {'center_x':0.5, 'center_y':0.8}
    MDTextField:
        id:search_bar
        hint_text: 'Search'
        helper_text_mode: 'on_focus'
        icon_right: 'account-search'
        # icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x':0.5, 'center_y':0.4}
        size_hint_x: None
        mode: "fill"
        fill_color: 1, 1, 1, 0.5
        # mode: "rectangle"
        # width:"300dp"
        size: "350dp", "10dp"
        # For the background colour
        # normal_color: 0, 0, 0, .5 # app.theme_cls.accent_color
        color_active: 1, 0, 1, 1
"""

image_toolbar = """
# FloatLayout:
ImageLeftWidget:
    pos:self.pos
    canvas:
        Ellipse:
            # pos: 15, 15
            size: 40 , 40 
            source: 'img/blank_user.png'
            angle_start: 0
            angle_end: 360
"""


class OtherUsersScreen(Screen):
    """Creates Screen to show all the other APP Users"""
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)

        self.name = "other_users"

        self.bottom_nav = Builder.load_string(users_toolbar)
        # self.bottom_nav = Builder.load_file('journeys.kv')

        self.add_widget(self.bottom_nav)


class UserBoxLayout(MDBoxLayout):
    """Aids in containing the list of users"""

    def refresh_callback(self, *args):
        '''A method that updates the state of your application
        while the spinner remains on the screen.'''
        # https://kivymd.readthedocs.io/en/latest/components/refresh-layout/
        def refresh_callback(interval):
            """Updates user list"""
            self.refresh_layout = self.ids['refresh_bar'] # For the RefreshLayout
            self.list_of_journeys = self.refresh_layout.clear_widgets()
            self.refresh_layout.add_widget(UsersList())
            self.refresh_layout.refresh_done()

        Clock.schedule_once(refresh_callback, 0.5)

class UsersList(MDList):
    """
    Creates the users list.
    Note This Info would come from the Database
    """

    def __init__(self, **kwargs):
        # Here were are going to modify the Drawer List items

        super(UsersList, self).__init__(**kwargs)

        self.users = None  # Initialize a journey Line

        # self.screen_manager = None

        self.clock = Clock.schedule_interval(self.initiate_users, 2)  # Call every 2 seconds


    def initiate_users(self, instance):
        """ Add our created Journeys"""

        self.users = user_list()
        self.clear_users()
        self.list_users()
        self.clock.cancel()

    def list_users(self):
        """ We add the users to the widget"""
        # We need to attach a name to picked journey
        # pos = [15, 15]
        for index, item in enumerate(self.users):
            user_name = item['username']

            # Using a custom Image
            image = ImageLeftWidget(source='img/blank_user.png')

            # Image right widget is not working in the source code
            item_image = OneLineAvatarListItem(text=user_name, on_press=self.picked_user)
            # # image.pos = item_image.pos
            item_image.add_widget(image)  # Here we add the image to the widget
            item_image.other_user_info = item   # Attach User Info

            self.add_widget(item_image)  # We add it the MDList Class

    def clear_users(self):
        """ We clear the Journeys that are added to the screen"""
        self.clear_widgets()

    def picked_user(self, instance):
        """When the user of the app chooses to see info of another user"""

        self.user_popup(instance)  # we pass the name
        pass

    def user_popup(self, instance):
        """ Popup for information in the Journey"""

        self.other_user_data = instance.other_user_info

        popup_info = (
            f"User name: {self.other_user_data['username']} \n"
            f"Journey ID: {self.other_user_data['email']} \n"
        )

        # Button to add
        close_dialogue = MDFlatButton(text="Close", on_release=self.close_dialog)

        # Dialog Widget

        self.dialog = MDDialog(
            title=instance.text, text=popup_info, buttons=[close_dialogue]
        )

        self.dialog.size_hint = [0.8, 0.8]
        self.dialog.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.dialog.open()

    def close_dialog(self, obj):
        """Close the Popup"""
        self.dialog.dismiss()  # To close the dialog box