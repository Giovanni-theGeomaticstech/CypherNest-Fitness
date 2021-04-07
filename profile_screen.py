from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder  # We are going to write .kv builders here
from kivymd.uix.button import MDRoundFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog  # Dialogue Parameter
from kivy.uix.boxlayout import BoxLayout

import calendar

# from KivyCalendar import CalendarWidget

from kivymd.uix.list import (
    OneLineListItem,
    MDList,
    IconLeftWidget,
    ImageRightWidget,
    OneLineIconListItem,
    OneLineAvatarListItem,
    ImageLeftWidget,
)  # Use the MDlist to add the other list items to

from kivy.clock import Clock

# Here we define the toolbar layout for our Application
# https://kivymd.readthedocs.io/en/latest/components/navigation-drawer/index.html
# https://kivymd.readthedocs.io/en/latest/components/toolbar/index.html


navigation_toolbar_helper = """
NavigationLayout:
    ScreenManager:
        Screen:
            BoxLayout: 
                orientation: 'vertical'
                MDToolbar:
                    title: "User Profile"
                    #menu,dots-vertical
                    # Used to all be 1 for Profile Screen now it is 0
                    left_action_items: [["menu", lambda x: app.get_running_app().root.screens[0].navigation_draw(), "Navigation Menu"]]
                    right_action_items: [["logout", lambda x: app.get_running_app().root.screens[0].logout()]] # Changed Screen Here used to be 1
                    elevation: 10 
                MDLabel:
                    text: "Under Development"
                    halign: 'center'
                # MDBottomAppBar:
                #     MDToolbar:
                #         title: "Help"
                #         left_action_items: [["coffee", lambda x: app.get_running_app().root.screens[0].navigation_draw()]]
                #         mode: 'free-end'
                #         type:'bottom'
                #         on_action_button: app.get_running_app().root.screens[0].navigation_draw()
                #         icon: 'language-python' 
                #         # elevation: 10
                Widget:
    ################################################
    MDNavigationDrawer:
        id: nav_drawer
        ContentNavigationDrawer:
            id: content_drawer
            orientation:"vertical"
            padding: "8dp"
            spacing: "8dp"
            ###########################
            # For Our User profile
            # Probably Move it into a class
            AnchorLayout:
                anchor_x: "left" #center
                size_hint_y: None
                height: avatar.height
               
                Image:
                    id: avatar
                    size_hint: None, None
                    size: "100dp", "100dp"
                    source: "img/blank_user.png"
        
            MDLabel:
                id: user_name
                text: "KivyMD library"
                font_style: "Button"
                size_hint_y: None
                height: self.texture_size[1]
                # pos_hint: {'center_x': 0.5}
        
            MDLabel:
                id: user_email
                text: 'test_email@gmail.com'
                font_style: "Caption"
                size_hint_y: None
                height: self.texture_size[1]
                # pos_hint: {'center_x': 0.5}
            ########################################
            ScrollView:
                NavMenuList:
                    id:md_list       
"""

# Create this first
class ProfileScreen(Screen):
    """Here We build the Navigation Layout of our Application.
        1. This page opens up after the user logs into the application
        2. Still Deciding on the different Features to Add in
        3. For Sure One is our Map (Probably use a different screen for this)
    """

    def __init__(self, **kwargs):

        # We are customizing Screen to our linking

        super(Screen, self).__init__(**kwargs)

        self.name = "Profile"

        self.toolbar = Builder.load_string(navigation_toolbar_helper)
        self.add_widget(self.toolbar)  # Here we build our toolbar

    def navigation_draw(self):
        screen_nav_elements = self.children[0].ids
        nav_drawer = screen_nav_elements["nav_drawer"].set_state(
            "open"
        )  # To open this item on the screen

        # This should update our user info once everything is already created
        Clock.schedule_once(self.update_user_info, 0.001)  # Update after 0.001 second

    def update_user_info(self, dt):
        screen_nav_elements = self.children[0].ids  # Current screen ids

        # RUN THIS ONCE EVERYTHING IS INITIALIZED

        user_email = screen_nav_elements["user_email"] # Place holder email content
        user_name = screen_nav_elements["user_name"] # Place holder user name
        
        running_app = MDApp.get_running_app().root

        if running_app.user:
            user_email.text = running_app.user["email"]
            user_name.text = running_app.user["username"]

    def logout(self):
        """
            To Logout fully we clear the temporary login file
            And then chnage to the Login screen
        """
        running_preface = MDApp.get_running_app()

        with open(running_preface.file_path, "w") as f:
                f.write("") # Empty the User token file
                f.close()
        running_app = MDApp.get_running_app().root
        running_app.current = "Login"

    def open_journeys_screen(self):
        """
                Here we want to change to the Journey List Screen
        """
        running_app = MDApp.get_running_app().root
        running_app.user_journeys = None  # We initialize this here
        running_app.current = "Journeys"

# Second
class ContentNavigationDrawer(BoxLayout):
    """ A Box Layout Class which contains the Information for our Navigation Menu"""
    pass

# Third
class NavMenuList(MDList):
    def __init__(self, **kwargs):
        """Develops the list of ELEMENTS FOR THE NAVIGATION MENU"""

        super(NavMenuList, self).__init__(**kwargs)

        # Menu icons
        icons_item = {
            # "folder": "My files",
            "account-multiple": "See other users",
            # "star": "Journey List",
            "map-clock": "Recent Journeys",  # Take us to Journey Screen
            "map-plus": "New Journey",
            # "upload": "Take Photo",  # For detection recognition
        }

        for item in icons_item:

            # Using a Built in Icon
            icon = IconLeftWidget(icon=item)

            if icons_item[item] == "See other users":
                item_ic = OneLineIconListItem(
                    text=icons_item[item], on_press=self.other_users_screen
                )
            elif icons_item[item] == "Recent Journeys":
                item_ic = OneLineIconListItem(
                    text=icons_item[item], on_press=self.open_journeys_screen
                )
            elif icons_item[item] == "New Journey":
                item_ic = OneLineIconListItem(
                    text=icons_item[item], on_press=self.new_journey_screen
                )

            else:
                item_ic = OneLineIconListItem(
                    text=icons_item[item], on_press=self.press_test
                )

            item_ic.add_widget(icon)  # Here we add the icon to the widget
            self.add_widget(item_ic)  # We add it the MDList Class

    def open_journeys_screen(self, instance):
        """
                Here we want to change to the Journey List Screen
        """
        running_app = MDApp.get_running_app().root
        running_app.user_journeys = None  # We initialize this here
        running_app.current = "Journeys"

    def new_journey_screen(self, instance):
        running_app = MDApp.get_running_app().root
        running_app.current = "MapView"

    def other_users_screen(self, instance):
        running_app = MDApp.get_running_app().root
        running_app.current = "other_users"

    def press_test(self, instance):
        """
        Here we want to change to the Screen
        """
        print("You Pressed me")