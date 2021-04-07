from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.button import MDRoundFlatButton, MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog  # Dialogue Parameter
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.graphics import Canvas, Color, Rectangle, RoundedRectangle
from kivy.clock import Clock


# Importing our Connection File
from connections import login, user_data

# These are in Python KV syntax
card_helper = """
MDCard:
        size_hint: None, None
        size: "350dp", "500dp"
        pos_hint: {"center_x": .5, "center_y": .5}
"""

#
image_toolbar = """
Image:
    size_hint_y: None
    size: 0,0
    pos_hint: {"center_x": 0.9, "center_y": .0}
    allow_stretch: True
    canvas:
        Ellipse:
            pos: self.pos
            source: 'img/blank_user.png'
            angle_start: 0
            angle_end: 360     
"""

username_helper = """
MDTextField:
        hint_text: 'Enter Username'
        helper_text: 'or click on forgot username'
        helper_text_mode: 'on_focus'
        icon_right: 'account-circle-outline'
        icon_right_color: app.theme_cls.primary_color
        pos_hint: {'center_x':0.58}#, 'center_y':0.6}
        # pos_hint: {'center_x':0.5, 'center_y':0.6}
        size_hint_x: None
        required: True
        multiline: True
        # mode: "rectangle"
        # width:"300dp"
        size: "300dp", "100dp"
        # For the background colour
        # normal_color: app.theme_cls.accent_color
        # color_active: 1, 0, 0, 1
"""

password_helper = """
MDTextField:
        id:password_text_field
        hint_text: 'Enter Password'
        helper_text: 'or click on forgot password'
        helper_text_mode: 'on_focus'
        icon_right: 'eye-off'
        icon_right_color: app.theme_cls.primary_color
        pos_hint: {'center_x':0.58}#, 'center_y':0.45}
        # pos_hint: {'center_x':0.5, 'center_y':0.45}
        size_hint_x: None
        required: True
        multiline: True
        # mode: "rectangle"
        # width:"300dp"
        size: "300dp", "100dp"
        password: True            
"""


class LoginScreen(Screen):
    """Here We are going to custom build our login Screen
        to stick mostly with Python implementation for Familiarity"""

    def __init__(self, **kwargs):

        # We are taking the Class from the library by doing this
        # This will allow us to customize it to our need

        super(Screen, self).__init__(**kwargs)

        # Set the screen name
        self.name = "Login"

        # Blank Image
        image = Builder.load_string(image_toolbar)

        # Make a BoxLayout
        box_layout = MDBoxLayout(
            spacing=25,
            size=("350dp", "400dp"),
            pos_hint={"center_y": 0.45},
            orientation="vertical",
            adaptive_size=True,
            adaptive_height=True,
            adaptive_width=True,
        )

        # Make our Submit button
        sign_in_button = MDRaisedButton(
            text="Sign In",
            md_bg_color=(0, 0, 0, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.58, "center_y": 0},
            on_release=self.submit_data,
        )
        sign_up_button = MDRaisedButton(
            text="Sign Up",
            md_bg_color=(0, 0, 0, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.58, "center_y": 0},
            on_release=self.sign_up,
        )

        self.card_layout = Builder.load_string(card_helper)
        self.username = Builder.load_string(username_helper)
        self.password = Builder.load_string(password_helper)

        box_layout.add_widget(image)
        box_layout.add_widget(self.username)
        box_layout.add_widget(self.password)
        box_layout.add_widget(sign_in_button)
        box_layout.add_widget(sign_up_button)

        self.card_layout.add_widget(box_layout)

        self.add_widget(self.card_layout)

        # For Logging in Automatically if previously logged in
        running_preface = MDApp.get_running_app()
        if running_preface.user_file_token:  # Pass the token saved in a file
            # print(running_preface.file_path)
            Clock.schedule_once(
                self.skip_login, 0.5
            )  # Here we skip the login after 1/2 a second

    def show_password(self):
        print(self.icon_right)

    def sign_up(self, instance):
        running_app = MDApp.get_running_app().root
        running_app.current = "Register"

    def submit_data(self, instance):
        profile_button = MDFlatButton(text="Open Profile", on_release=self.close_dialog)

        # Add the buttons field to add buttons to dialog
        self.dialog = MDDialog(
            title="User Validation", size_hint=[0.7, 1], buttons=[profile_button]
        )

        self.success = False  # For successful login

        self.login_token = login(
            self.username.text, self.password.text
        )  # login interface

        # SO SOME REQUEST FUNCTIONS
        if self.login_token:
            self.dialog.title = "Successful User Login"
            self.dialog.text = f"Good day {self.username.text}"
            self.success = True
            self.username.text = ""
            self.password.text = ""
            self.update_user_token_file(self.login_token)
        else:
            self.dialog.title = "Error with User Login"
            self.dialog.text = "User Note Found. Please re-enter Password or Username"
            self.success = False
            self.username.text = ""
            self.password.text = ""

        self.dialog.open()  # To open our dialog without adding to screen

    def close_dialog(self, obj):
        self.dialog.dismiss()  # To close the dialog box

        if self.success:
            running_app = MDApp.get_running_app().root
            running_app.user_token = self.login_token  # The User Login Token
            running_app.user = user_data(self.login_token)

            # Change Screen to profile Screen
            running_app.current = "Profile"

    def update_user_token_file(self, new_token):
        # Update Automatic login file with an access token
        # Overwrites Previous login data
        running_preface = MDApp.get_running_app()

        with open(running_preface.file_path, "w") as f:
            f.write(new_token)
            f.close()

    def skip_login(self, dt):
        """Skip Submitting Login Data
            Why? 
                - If A User is already logged into the system 
                - We do not want constant relogin attempts
        """
        running_preface = MDApp.get_running_app()
        running_app = MDApp.get_running_app().root
        running_app.user_token = running_preface.user_file_token  # The User Login Token
        running_app.user = user_data(running_preface.user_file_token)

        # {'detail': 'Invalid token.'} That is the message for expired token
        # Your token Lasts for only 10 hours
        if (
            "detail" in running_app.user.keys()
        ):  # If token has expired do not change page
            pass
        else:
            running_app.current = "Profile"
