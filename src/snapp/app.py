import os
import requests
import uuid
from datetime import datetime, timedelta

import toga
from toga import Image, ImageView
from toga.style import Pack

from snapp.services.local_db import (
    setup_local_database,
    insert_entry,
    get_all_entries,
    get_unsynced_entries,
    mark_entry_as_synced
)
from snapp.services.firestore_sync import upload_to_firestore, fetch_from_firestore
from snapp.services.auth import sign_in_with_email_password
from snapp.utils.net_utils import is_online
from snapp.screens.instructions import build_instructions_screen
from snapp.screens.followup import build_followup_screen
from snapp.screens.visualization import build_visualization_screen
from snapp.screens.login import build_login_screen
from snapp.screens.goal_type import build_goal_type_screen
from snapp.screens.time_span import build_time_span_screen
from snapp.screens.settings import build_settings_screen
from snapp.services.settings_sync import load_settings_from_firestore

class ActivityLogger(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.user_token = None
        self.main_window.content = build_login_screen(self)
        self.main_window.show()

    def save_data(self, x_label, y_label, note=None):
        timestamp = datetime.now().isoformat()
        entry = {
            "goal_type": y_label,
            "time_frame": x_label,
            "note": note or "",
            "timestamp": timestamp
        }
        try:
            insert_entry(self.cursor, self.conn, entry)
            if is_online() and self.user_token:
                if upload_to_firestore(self.user_token, entry):
                    mark_entry_as_synced(self.cursor, self.conn, timestamp)
        except Exception as e:
            print("❌ Error saving data:", e)

    def load_data(self):
        if not hasattr(self, "cursor") or self.cursor is None:
            print("⚠️ Cannot load data — SQLite cursor not initialized yet.")
            self.data = []
            return
        try:
            self.data = get_all_entries(self.cursor)
            if is_online() and self.user_token:
                firestore_entries = fetch_from_firestore(self.user_token)
                existing_ts = {entry["timestamp"] for entry in self.data if entry.get("timestamp")}
                new_entries = [e for e in firestore_entries if e.get("timestamp") not in existing_ts]
                self.data.extend(new_entries)
        except Exception as e:
            print("⚠️ Failed to load data:", e)
            self.data = []

    def sync_offline_data(self):
        if not is_online() or not self.user_token:
            print("⚠️ Cannot sync data. Offline or missing token.")
            return
        for entry in get_unsynced_entries(self.cursor):
            entry_id, goal_type, time_frame, note, timestamp = entry
            try:
                if upload_to_firestore(self.user_token, {
                    "goal_type": goal_type,
                    "time_frame": time_frame,
                    "note": note,
                    "timestamp": timestamp
                }):
                    mark_entry_as_synced(self.cursor, self.conn, entry_id)
            except Exception as e:
                print(f"❌ Error syncing entry {entry_id}: {e}")

    def show_goal_type_screen(self, widget=None):
        self.current_screen = build_goal_type_screen(self)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def handle_goal_type_selection(self, selected_goal_type):
        self.selected_goal_type = selected_goal_type
        self.show_time_span_screen(selected_goal_type)

    def handle_time_frame_selection(self, selected_time_frame, goal_type):
        self.save_data(selected_time_frame, goal_type)
        self.show_followup_screen(selected_time_frame, goal_type)

    def handle_grid_selection(self, x_label, y_label):
        self.save_data(x_label, y_label)
        self.show_followup_screen(x_label, y_label)

    def show_instructions_screen(self, widget=None):
        self.current_screen = build_instructions_screen(self)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def show_followup_screen(self, x_label, y_label, widget=None):
        self.last_x_label = x_label
        self.last_y_label = y_label
        self.current_screen = build_followup_screen(self, x_label, y_label)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def show_time_span_screen(self, selected_goal_type):
        self.current_screen = build_time_span_screen(self, selected_goal_type)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def show_login_screen(self, widget=None):
        self.current_screen = build_login_screen(self)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def show_settings_screen(self, widget=None, back_action=None):
        self.current_screen = build_settings_screen(self, back_action=back_action)
        self.main_window.content = self.current_screen

    def show_visualization_screen(self, widget=None):
        if not hasattr(self, 'reference_date'):
            self.reference_date = datetime.now()
        self.current_screen = build_visualization_screen(self)
        self.main_window.content = self.current_screen

    def apply_filter(self, widget):
        self.load_data()
        if widget.value != "All":
            self.data = [e for e in self.data if e.get("time_frame") == widget.value]
        self.show_visualization_screen()

    def group_entries(self, data, category):
        counts = {}
        for entry in data:
            key = entry.get(category, "Unknown")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def get_time_offset(self):
        if self.timeframe_dropdown.value == "Daily": return timedelta(days=1)
        if self.timeframe_dropdown.value == "Weekly": return timedelta(weeks=1)
        if self.timeframe_dropdown.value == "Monthly": return timedelta(days=30)
        if self.timeframe_dropdown.value == "Yearly": return timedelta(days=365)
        return timedelta(days=0)

    def reset_reference_to_latest(self):
        if not self.data:
            self.reference_date = datetime.now()
            return
        try:
            latest = max(self.data, key=lambda x: datetime.fromisoformat(x["timestamp"]) if x.get("timestamp") else datetime.min)
            self.reference_date = datetime.fromisoformat(latest["timestamp"])
        except Exception as e:
            print("⚠️ Could not determine latest reference date:", e)
            self.reference_date = datetime.now()

    def filter_data_by_timeframe(self, timeframe, reference_date=None):
        if not reference_date:
            reference_date = datetime.now()
        filtered = []
        for entry in self.data:
            ts = entry.get("timestamp")
            if not ts:
                continue
            try:
                date = datetime.fromisoformat(ts)
            except ValueError:
                continue
            if timeframe == "Daily" and date.date() == reference_date.date():
                filtered.append(entry)
            elif timeframe == "Weekly":
                sow = reference_date - timedelta(days=reference_date.weekday())
                eow = sow + timedelta(days=6)
                if sow.date() <= date.date() <= eow.date():
                    filtered.append(entry)
            elif timeframe == "Monthly" and (date.year == reference_date.year and date.month == reference_date.month):
                filtered.append(entry)
            elif timeframe == "Yearly" and date.year == reference_date.year:
                filtered.append(entry)
        return filtered

    
    def update_chart_only(self, widget):
        from toga import ImageView, Label, Box
        from toga.style import Pack
        import gc, os
    
        if not hasattr(self, "chart_type_dropdown") or not hasattr(self, "timeframe_dropdown"):
            print("⚠️ Dropdowns not initialized yet.")
            return
    
        # 🔁 Replace chart container completely
        new_chart_container = Box(style=Pack(direction="column", padding=5))
        self.chart_container_parent.remove(self.chart_container)
        self.chart_container = new_chart_container
        self.chart_container_parent.add(self.chart_container)
    
        def format_reference_range():
            date = self.reference_date
            if self.timeframe == "Daily":
                return f"Data Range: {date.strftime('%m/%d/%Y')} to {date.strftime('%m/%d/%Y')}"
            elif self.timeframe == "Weekly":
                start = date - timedelta(days=date.weekday())
                end = start + timedelta(days=6)
                return f"Data Range: {start.strftime('%m/%d/%Y')} to {end.strftime('%m/%d/%Y')}"
            elif self.timeframe == "Monthly":
                start = date.replace(day=1)
                end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                return f"Data Range: {start.strftime('%m/%d/%Y')} to {end.strftime('%m/%d/%Y')}"
            elif self.timeframe == "Yearly":
                start = date.replace(month=1, day=1)
                end = date.replace(month=12, day=31)
                return f"Data Range: {start.strftime('%m/%d/%Y')} to {end.strftime('%m/%d/%Y')}"
            return "Data Range: Unknown"
    
        self.chart_container.add(Label(format_reference_range(), style=Pack(font_size=14, padding=(5, 5, 10, 5))))
    
        filtered = self.filter_data_by_timeframe(self.timeframe, self.reference_date)
    
        if hasattr(self, "goal_chart_widget"):
            self.goal_chart_widget = None
        if hasattr(self, "time_chart_widget"):
            self.time_chart_widget = None
        if hasattr(self, "last_chart_file_path") and self.last_chart_file_path:
            try:
                gc.collect()
                os.remove(self.last_chart_file_path)
                print(f"🧹 Deleted previous chart file: {self.last_chart_file_path}")
            except Exception as e:
                print("⚠️ Could not delete old chart file:", e)
    
        if not filtered:
            self.chart_container.add(Label("No data for this time period.", style=Pack(font_size=14, padding=10)))
    
        else:
            goal_chart, path = self.generate_activity_chart(filtered, self.chart_type, "goal_type")
            time_chart, _ = self.generate_activity_chart(filtered, self.chart_type, "time_frame")
            self.last_chart_file_path = path
    
            self.goal_chart_widget = ImageView(goal_chart, style=Pack(width=300, height=300, padding=5))
            self.time_chart_widget = ImageView(time_chart, style=Pack(width=300, height=300, padding=5))
    
            self.chart_container.add(Label("🎯 Goal-Type Breakdown", style=Pack(font_size=16, padding_bottom=5, padding_top=10)))
            self.chart_container.add(self.goal_chart_widget)
            self.chart_container.add(Label("⏳ Time-Span Breakdown", style=Pack(font_size=16, padding_bottom=5, padding_top=10)))
            self.chart_container.add(self.time_chart_widget)
    
        self.prev_button.enabled = any(datetime.fromisoformat(e["timestamp"]) < self.reference_date for e in self.data if "timestamp" in e)
        self.next_button.enabled = any(datetime.fromisoformat(e["timestamp"]) > self.reference_date for e in self.data if "timestamp" in e)
    


    def generate_activity_chart(self, data, chart_type, category):
        grouped = self.group_entries(data, category)
        if chart_type == "Bar":
            from snapp.charts.bar_chart import generate_bar_chart_image
            img = generate_bar_chart_image(grouped, category_type="goal" if category == "goal_type" else "time")
        elif chart_type == "Pie":
            from snapp.charts.pie_chart import generate_pie_chart_image
            img = generate_pie_chart_image(grouped, category_type="goal" if category == "goal_type" else "time")
        else:
            return None, None
        filename = f"chart_{uuid.uuid4().hex}.png"
        path = os.path.join(os.path.dirname(__file__), filename)
        img.save(path)
        return Image(path), path


    def show_previous_timeframe(self, widget):
        offset = self.get_time_offset()
        current = self.reference_date
        earliest = min((datetime.fromisoformat(e["timestamp"]) for e in self.data if "timestamp" in e), default=datetime.min)
    
        while current > earliest:
            current -= offset
            filtered = self.filter_data_by_timeframe(self.timeframe, current)
            if filtered:
                self.reference_date = current
                self.update_chart_only(widget)
                return
    
        # If no earlier frame found
        self.prev_button.enabled = False
        self.update_chart_only(widget)

    def show_next_timeframe(self, widget):
        offset = self.get_time_offset()
        current = self.reference_date
        latest = max((datetime.fromisoformat(e["timestamp"]) for e in self.data if "timestamp" in e), default=datetime.max)
    
        while current < latest:
            current += offset
            filtered = self.filter_data_by_timeframe(self.timeframe, current)
            if filtered:
                self.reference_date = current
                self.update_chart_only(widget)
                return
    
        self.next_button.enabled = False
        self.update_chart_only(widget)



    def update_chart_from_dropdown(self, widget):
        if not hasattr(self, "chart_type_dropdown") or not hasattr(self, "timeframe_dropdown"):
            print("⚠️ Dropdowns not initialized yet.")
            return
        
        self.load_data()
        self.reset_reference_to_latest()
        self.timeframe = self.timeframe_dropdown.value
        self.chart_type = self.chart_type_dropdown.value
        self.update_chart_only(widget)

    def after_login_success(self, user_data):
        self.user_token = user_data.get("idToken")
        self.user_email = user_data.get("email", "Unknown Email")
        self.user_id = user_data.get("localId")
        self.conn, self.cursor = setup_local_database(self)
        try:
            self.nudge_settings = load_settings_from_firestore(self.user_token, self.user_id)
        except Exception as e:
            print("⚠️ Error loading settings:", e)
            self.nudge_settings = {}
        self.load_data()
        self.sync_offline_data()
        self.show_instructions_screen()

def main():
    return ActivityLogger()

if __name__ == "__main__":
    main().main_loop()
