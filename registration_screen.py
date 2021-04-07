from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog  # Dialogue Parameter
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.graphics import Canvas, Color, Rectangle

# Importing our Connection File
from connections import login, user_data, registration

# These are in Python KV syntax
card_helper = """
MDCard:
        size_hint: None, None
        size: "350dp", "500dp"
        pos_hint: {"center_x": .5, "center_y": .5}
"""

image_toolbar = """
Image:
    size_hint_y: None
    size: 0,0
    pos_hint: {"center_x": 0.9, "center_y": 0}
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
        size: "300dp", "100dp"
        # For the background colour
        # normal_color: app.theme_cls.accent_color
        # color_active: 1, 0, 0, 1
"""

firstname_helper = """
MDTextField:
        hint_text: 'Enter Firstname'
        helper_text: 'or click on forgot username'
        helper_text_mode: 'on_focus'
        icon_right: 'form-textbox'
        icon_right_color: app.theme_cls.primary_color
        pos_hint: {'center_x':0.58}#, 'center_y':0.6}
        size_hint_x: None
        required: True
        multiline: True
        size: "300dp", "100dp"
        # For the background colour
        # normal_color: app.theme_cls.accent_color
        # color_active: 1, 0, 0, 1
"""
lastname_helper = """
MDTextField:
        hint_text: 'Enter Lastname'
        helper_text: 'or click on forgot username'
        helper_text_mode: 'on_focus'
        icon_right: 'form-textbox'
        icon_right_color: app.theme_cls.primary_color
        pos_hint: {'center_x':0.58}#, 'center_y':0.6}
        # pos_hint: {'center_x':0.5, 'center_y':0.6}
        size_hint_x: None
        required: True
        multiline: True
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
        size: "300dp", "100dp"
        password: True
"""

email_helper = """
MDTextField:
        id:email_text_field
        hint_text: 'Enter Email'
        helper_text: 'or click on forgot password'
        helper_text_mode: 'on_focus'
        icon_right: 'at'
        icon_right_color: app.theme_cls.primary_color
        pos_hint: {'center_x':0.58}#, 'center_y':0.45}
        # pos_hint: {'center_x':0.5, 'center_y':0.45}
        size_hint_x: None
        required: True
        multiline: True
        size: "300dp", "100dp"
"""

class RegisterScreen(Screen):
    """Here We are going to custom build our login Screen
        to stick mostly with Python implementation for Familiarity"""

    def __init__(self, **kwargs):

        # We are taking the Class from the library by doing this
        # This will allow us to customize it to our need

        super(Screen, self).__init__(**kwargs)

        # Name the Screen
        self.name = "Register"

        # Blank Image
        image = Builder.load_string(image_toolbar)

        # Make a BoxLayout
        box_layout = MDBoxLayout(
            spacing=10,
            size=("350dp", "400dp"),
            pos_hint={"center_y": 0.45},
            orientation='vertical',
            adaptive_size=True,
            adaptive_height=True,
            adaptive_width=True,
        )

        # Make our Submit button
        register_button = MDRaisedButton(
            text="Register",
            md_bg_color=(0, 0, 0, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.58, "center_y": 0},
            on_release=self.submit_data,
        )

        go_to_login_button = MDRaisedButton(
            text="Return to Login Screen",
            md_bg_color=(0, 0, 0, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.58, "center_y": 0},
            on_release=self.go_to_login,
        )

        self.card_layout = Builder.load_string(card_helper)
        self.firstname = Builder.load_string(firstname_helper)
        self.lastname = Builder.load_string(lastname_helper)
        self.username = Builder.load_string(username_helper)
        self.password = Builder.load_string(password_helper)
        self.email = Builder.load_string(email_helper)

        box_layout.add_widget(image)
        box_layout.add_widget(self.firstname)
        box_layout.add_widget(self.lastname)
        box_layout.add_widget(self.username)
        box_layout.add_widget(self.password)
        box_layout.add_widget(self.email)
        box_layout.add_widget(register_button)
        box_layout.add_widget(go_to_login_button)

        self.card_layout.add_widget(box_layout)

        self.add_widget(self.card_layout)

    def submit_data(self, instance):
        go_to_login_button = MDFlatButton(text="Go to Login", on_release=self.close_dialog)
        close_button = MDFlatButton(text="Close", on_release=self.close_dialog)

        # Add the buttons field to add buttons to dialog
        self.dialog = MDDialog(
            title="User Validation",
            size_hint=[0.7, 1],
            buttons=[go_to_login_button, close_button],
        )

        self.success = False  # For successful login

        if self.username.text and self.email and self.password:
            self.registration_success = registration(
                username=self.username.text,
                email=self.email.text,
                password=self.password.text,
                firstname=self.firstname.text,
                lastname=self.lastname.text
            )  # registration interface

            # SO SOME REQUEST FUNCTIONS
            errors = "errors" not in list(self.registration_success.json())
            if not errors: # True
                error_json = self.registration_success.json()['errors']
        else:
            self.registration_success = False
            errors = False
            error_json = {"Data": 'Fields were not filled'}

        if self.registration_success and errors:
            self.dialog.title = "Successful User Registration"
            self.dialog.text = f"Good day {self.username.text}"
            self.success = True
            self.username.text = ""
            self.password.text = ""
            self.email.text = ""
            self.firstname.text = ""
            self.lastname.text = ""
        else:
            self.dialog.title = "Error with User Registration"
            self.dialog.text = f"User Error:{error_json}"
            self.success = False
            self.username.text = ""
            self.password.text = ""
            self.email.text = ""
            self.firstname.text = ""
            self.lastname.text = ""

        self.dialog.open()  # To open our dialog without adding to screen

    def go_to_login(self, instance):
        running_app = MDApp.get_running_app().root
        # Go to login page
        running_app.current = "Login"

    def close_dialog(self, obj):
        self.dialog.dismiss()  # To close the dialog box

        if self.success:
            self.go_to_login(instance=None)
           
