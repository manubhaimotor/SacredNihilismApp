from snapp.services.settings_sync import load_settings_from_firestore
from snapp.services.local_db import setup_local_database

class UserController:
    def __init__(self, app):
        self.app = app

    def after_login_success(self, user_data):
        self.app.user_token = user_data.get("idToken")
        self.app.user_email = user_data.get("email", "Unknown Email")
        self.app.user_id = user_data.get("localId")
        self.app.conn, self.app.cursor = setup_local_database(self.app)
        try:
            self.app.nudge_settings = load_settings_from_firestore(self.app.user_token, self.app.user_id)
        except Exception as e:
            print("⚠️ Error loading settings:", e)
            self.app.nudge_settings = {}
        self.app.data = []
        self.app.data_controller.load_data()
        self.app.data_controller.sync_offline_data()
        self.app.navigation.show_instructions_screen()
        self.app.screen_history = []
        self.app.forward_stack = []
        self.app.has_logged_in = True
