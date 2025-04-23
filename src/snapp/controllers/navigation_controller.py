from datetime import datetime
from snapp.screens.goal_type import build_goal_type_screen
from snapp.screens.time_span import build_time_span_screen
from snapp.screens.followup import build_followup_screen
from snapp.screens.visualization import build_visualization_screen
from snapp.screens.settings import build_settings_screen
from snapp.screens.instructions import build_instructions_screen
from snapp.screens.login import build_login_screen

class NavigationController:
    def __init__(self, app):
        self.app = app

    def set_screen(self, new_screen):
        if getattr(self.app, "has_logged_in", False):
            if getattr(self.app, "current_screen", None):
                self.app.screen_history.append(self.app.current_screen)
                self.app.forward_stack.clear()
        self.app.current_screen = new_screen
        self.app.main_window.content = new_screen

    def go_back(self, widget=None):
        if getattr(self.app, "screen_history", []):
            last = self.app.screen_history.pop()
            self.app.forward_stack.append(self.app.current_screen)
            self.set_screen(last)

    def go_forward(self, widget=None):
        if getattr(self.app, "forward_stack", []):
            next_screen = self.app.forward_stack.pop()
            self.app.screen_history.append(self.app.current_screen)
            self.set_screen(next_screen)

    def show_goal_type_screen(self, widget=None):
        self.set_screen(build_goal_type_screen(self.app))

    def show_time_span_screen(self, selected_goal_type):
        self.set_screen(build_time_span_screen(self.app, selected_goal_type))

    def show_followup_screen(self, x_label, y_label, widget=None):
        self.app.last_x_label = x_label
        self.app.last_y_label = y_label
        self.set_screen(build_followup_screen(self.app, x_label, y_label))

    def show_visualization_screen(self, widget=None):
        if not hasattr(self.app, 'reference_date'):
            self.app.reference_date = datetime.now()
        self.set_screen(build_visualization_screen(self.app))

    def show_settings_screen(self, widget=None, back_action=None):
        self.set_screen(build_settings_screen(self.app, back_action=back_action))

    def show_instructions_screen(self, widget=None):
        self.set_screen(build_instructions_screen(self.app))

    def show_login_screen(self, widget=None):
        self.app.current_screen = build_login_screen(self.app)
        self.app.main_window.content = self.app.current_screen
