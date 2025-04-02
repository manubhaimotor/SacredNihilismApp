# snapp/screens/signup.py

import toga
from toga import Box, Label, TextInput, Button
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

class SignupScreen:
    def __init__(self, app):
        self.app = app
        self.error_label = Label('', style=Pack(color='red', padding_top=5))

        self.email_input = TextInput(placeholder='Email', style=Pack(width=250, padding=5))
        self.password_input = TextInput(placeholder='Password', style=Pack(width=250, padding=5))
        self.password_input.secure = True

        self.signup_button = Button("Create Account", on_press=self.handle_signup, style=Pack(padding=5, width=150))
        self.back_to_login_button = Button("Back to Login", on_press=self.back_to_login, style=Pack(padding=5))

        self.main_box = Box(
            children=[
                Label('Create New Account', style=Pack(font_size=20, padding_bottom=10)),
                self.email_input,
                self.password_input,
                self.signup_button,
                self.back_to_login_button,
                self.error_label,
            ],
            style=Pack(direction=COLUMN, alignment=CENTER, padding=50)
        )

    def get_root_widget(self):
        return toga.ScrollContainer(content=self.main_box)
        
    async def handle_signup(self, widget):
        email = self.email_input.value.strip()
        password = self.password_input.value.strip()

        if not email or not password:
            self.error_label.text = "❌ Email and password required."
            return

        try:
            from snapp.services.auth import sign_up_with_email_password
            id_token = sign_up_with_email_password(email, password)

            if id_token:
                self.app.after_login_success(id_token)
            else:
                self.error_label.text = "❌ Could not create account."
        except Exception as e:
            self.error_label.text = "❌ Sign up failed. Try again."
            print("❌ Exception during signup:", e)


    def back_to_login(self, widget):
        from snapp.screens.login import LoginScreen
        self.app.main_window.content = LoginScreen(self.app).get_root_widget()
