import toga
from toga.style import Pack
from snapp.screens.login import build_login_screen

from snapp.controllers.navigation_controller import NavigationController
from snapp.controllers.chart_controller import ChartController
from snapp.controllers.data_controller import DataController
from snapp.controllers.user_controller import UserController

class ActivityLogger(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.user_token = None

        # Inject controllers
        self.navigation = NavigationController(self)
        self.charts = ChartController(self)
        self.data_controller = DataController(self)
        self.user = UserController(self)

        self.main_window.content = build_login_screen(self)
        self.main_window.show()
        
    def after_login_success(self, user_data):
        return self.user.after_login_success(user_data)
    
    def update_chart_only(self, widget):
        return self.charts.update_chart_only(widget)
    
    def update_chart_from_dropdown(self, widget):
        return self.charts.update_chart_from_dropdown(widget)
    
    def show_previous_timeframe(self, widget):
        return self.charts.show_previous_timeframe(widget)
    
    def show_next_timeframe(self, widget):
        return self.charts.show_next_timeframe(widget)
    
    def handle_time_frame_selection(self, tf, goal_type):
        return self.data_controller.handle_time_frame_selection(tf, goal_type)
    
    def save_data(self, x, y, note=None):
        return self.data_controller.save_data(x, y, note)
    
    def load_data(self):
        return self.data_controller.load_data()
    
    def sync_offline_data(self):
        return self.data_controller.sync_offline_data()
    
    # Screen shortcuts
    def show_goal_type_screen(self, widget=None):
        return self.navigation.show_goal_type_screen(widget)
    
    def show_time_span_screen(self, goal_type):
        return self.navigation.show_time_span_screen(goal_type)
    
    def show_followup_screen(self, x, y, widget=None):
        return self.navigation.show_followup_screen(x, y, widget)
    
    def show_visualization_screen(self, widget=None):
        return self.navigation.show_visualization_screen(widget)
    
    def show_settings_screen(self, widget=None, back_action=None):
        return self.navigation.show_settings_screen(widget, back_action)
    
    def show_instructions_screen(self, widget=None):
        return self.navigation.show_instructions_screen(widget)
    
    def show_login_screen(self, widget=None):
        return self.navigation.show_login_screen(widget)
    
    def go_back(self, widget=None):
        return self.navigation.go_back(widget)

    def go_forward(self, widget=None):
        return self.navigation.go_forward(widget)
    
    def handle_goal_type_selection(self, selected_goal_type):
        return self.data_controller.handle_goal_type_selection(selected_goal_type)

    def reset_reference_to_latest(self):
        return self.charts.reset_reference_to_latest()



def main():
    return ActivityLogger()

if __name__ == "__main__":
    main().main_loop()