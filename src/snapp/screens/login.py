import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, CENTER, RIGHT
import asyncio
import requests
from snapp.services.auth import sign_in_with_email_password
from snapp.services.settings_sync import load_settings_from_firestore


FIREBASE_WEB_API_KEY = "AIzaSyAse0jNdrq0LBu33fJc6WzoF6XovI2OyDQ"


def build_login_screen(app):
    main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=40))

    main_box.add(toga.Label("Login", style=Pack(font_size=24, font_weight="bold", padding_bottom=20)))

    email_input = toga.TextInput(placeholder="Email", style=Pack(padding_bottom=10, width=300))
    password_input = toga.PasswordInput(placeholder="Password", style=Pack(padding_bottom=10, width=300))
    main_box.add(email_input)
    main_box.add(password_input)

    # Loading and error UI
    loading_label = toga.Label("Logging in... (takes ~5 seconds)", style=Pack(padding_top=5, padding_bottom=5))
    
       
    error_label = toga.Label("", style=Pack(color="red", padding_bottom=5))
    main_box.add(error_label)
    error_label.visible = False
    
    

    async def handle_login(widget):
        if loading_label not in main_box.children:
            main_box.insert(2, loading_label)  # insert after password_input
    
        login_btn.enabled = False
        loading_label.visible = True
        error_label.visible = False
        error_label.text = ""
    
        email = email_input.value
        password = password_input.value
    
        try:
            user_info = await asyncio.to_thread(sign_in_with_email_password, email, password)
            app.user_token = user_info["idToken"]
            app.user_id = user_info["localId"]
            app.user_email = email
    
            app.nudge_settings = load_settings_from_firestore(app.user_token, app.user_id)
            print("✅ Login successful. Settings loaded:", app.nudge_settings)
    
            app.after_login_success(user_info)
    
        except Exception as e:
            print("❌ Login failed:", e)
            error_label.text = "Invalid email or password"
            error_label.visible = True
            await app.main_window.dialog(
                toga.ErrorDialog("Login Failed", "Check your credentials and try again.")
            )
    
        finally:
            loading_label.visible = False
            login_btn.enabled = True


    async def handle_forgot_password(widget):
        email = email_input.value.strip()
        if not email:
            await app.main_window.dialog(
                toga.ErrorDialog("Missing Email", "Please enter your email before requesting a reset.")
            )
            return

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            await app.main_window.dialog(
                toga.InfoDialog("Reset Email Sent", "Check your inbox to reset your password.")
            )
            print("📧 Password reset email sent to:", email)
        except Exception as e:
            print("❌ Failed to send password reset:", e)
            await app.main_window.dialog(
                toga.ErrorDialog("Error", "Could not send reset email. Try again later.")
            )

    def show_signup_screen(widget):
        from snapp.screens.signup import SignupScreen
        app.main_window.content = SignupScreen(app).get_root_widget()

    # Buttons
    nonlocal_login_btn = toga.Button("Log In", on_press=handle_login, style=Pack(padding_top=10, width=300))
    forgot_btn = toga.Button("Forgot Password?", on_press=handle_forgot_password, style=Pack(padding_top=5, width=300))
    signup_btn = toga.Button("Create Account", on_press=show_signup_screen, style=Pack(padding_top=10, width=300))

    login_btn = nonlocal_login_btn  # Needed for scope access inside handler
    main_box.add(login_btn)
    main_box.add(forgot_btn)
    main_box.add(signup_btn)

    return toga.ScrollContainer(content=main_box)
