import toga
from toga import Box, Label, TextInput, Button
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

class LoginScreen:
    def __init__(self, app):
        self.app = app
        self.error_label = Label('', style=Pack(color='red', padding_top=5))

        self.email_input = TextInput(placeholder='Email', style=Pack(width=250, padding=5))
        self.password_input = TextInput(placeholder='Password', style=Pack(width=250, padding=5))
        self.password_input.secure = True
        self.login_button = Button("Login", on_press=self.handle_login, style=Pack(padding=5, width=100))
        self.signup_button = Button("Create Account", on_press=self.show_signup_screen, style=Pack(padding=5))           

        self.main_box = Box(
            children=[
                Label('Sacred Nihilism Login', style=Pack(font_size=20, padding_bottom=10)),
                self.email_input,
                self.password_input,
                self.login_button,
                self.signup_button,  # ✅ Add this line
                self.error_label,
            ],
            style=Pack(direction=COLUMN, alignment=CENTER, padding=50)
        )


    def get_root_widget(self):
        return self.main_box

    async def handle_login(self, widget):
        email = self.email_input.value.strip()
        password = self.password_input.value.strip()
        if not email or not password:
            self.error_label.text = "❌ Email and password required."
            return

        from snapp.services.auth import sign_in_with_email_password

        try:
            id_token = sign_in_with_email_password(email, password)
            if id_token:
                self.app.after_login_success(id_token)
            else:
                print("❌ Firebase Login Failed: No token returned.")
                self.error_label.text = "❌ Invalid credentials."

        except Exception as e:
            self.error_label.text = "❌ Login failed. Please try again."
            print("❌ Exception during login:", e)

            
    def show_signup_screen(self, widget):
        from snapp.screens.signup import SignupScreen
        self.app.main_window.content = SignupScreen(self.app).get_root_widget()

