import os
import requests
from snapp.services.local_db import (
    setup_local_database,
    insert_entry,
    get_all_entries,
    get_unsynced_entries,
    mark_entry_as_synced
)
from snapp.services.firestore_sync import upload_to_firestore, fetch_from_firestore
from snapp.utils.net_utils import is_online
from snapp.screens.instructions import build_instructions_screen
from snapp.screens.followup import build_followup_screen
from snapp.screens.visualization import build_visualization_screen
from snapp.screens.login import LoginScreen


# ✅ Firebase API Credentials
FIREBASE_WEB_API_KEY = "AIzaSyAse0jNdrq0LBu33fJc6WzoF6XovI2OyDQ"
FIREBASE_PROJECT_ID = "sacred-nihilism"
FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/sacred-nihilism/databases/(default)/documents/activity_logs"


from snapp.services.auth import sign_in_with_email_password
import toga
from toga import Image
# Save to temporary file
import uuid
from datetime import datetime, timedelta


class ActivityLogger(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.user_token = None  # will be set on successful login
        self.main_window.content = LoginScreen(self).get_root_widget()
        self.main_window.show()

      
    def save_data(self, x_label, y_label, note=None):
        """Save activity log to SQLite and sync to Firestore when online."""
        timestamp = datetime.now().isoformat()

        entry = {
            "goal_type": y_label,
            "time_frame": x_label,
            "note": note if note else "",
            "timestamp": timestamp
        }

        try:
            # ✅ Save locally to SQLite
            insert_entry(self.cursor, self.conn, entry)

            # ✅ Sync to Firestore if online and authenticated
            if is_online() and self.user_token:
                success = upload_to_firestore(self.user_token, entry)
                if success:
                    mark_entry_as_synced(self.cursor, self.conn, timestamp)
               
        except Exception as e:
            print("❌ Error saving data:", e)


    def load_data(self):
        """Load stored activity logs from SQLite and Firestore."""
        try:
            # ✅ Load from SQLite first
            rows = get_all_entries(self.cursor)
            self.data = rows
            print("✅ Data loaded from SQLite:", self.data)

            if is_online() and self.user_token:
                firestore_entries = fetch_from_firestore(self.user_token)

                # Deduplicate using timestamp string
                existing_ts = {entry["timestamp"] for entry in self.data if entry.get("timestamp")}
                new_entries = [entry for entry in firestore_entries if entry.get("timestamp") not in existing_ts]

                self.data.extend(new_entries)
                print(f"📦 Final data loaded: {len(self.data)} entries")


        except Exception as e:
            print("⚠️ Failed to load data:", e)
            self.data = []

    
    def sync_offline_data(self):
        """Sync unsynced data from SQLite to Firestore."""
        if not is_online():
            print("⚠️ Offline: Cannot sync data.")
            return

        if not self.user_token:
            print("❌ No valid Firebase user token. Cannot sync.")
            return

        unsynced_entries = get_unsynced_entries(self.cursor)

        for entry in unsynced_entries:
            entry_id, goal_type, time_frame, note, timestamp = entry

            try:
                success = upload_to_firestore(self.user_token, {
                    "goal_type": goal_type,
                    "time_frame": time_frame,
                    "note": note,
                    "timestamp": timestamp
                })

                if success:
                    mark_entry_as_synced(self.cursor, self.conn, entry_id)

            except Exception as e:
                print(f"❌ Error syncing entry {entry_id}: {e}")

    def show_goal_type_screen(self, widget=None):
        from snapp.screens.goal_type import build_goal_type_screen
        self.current_screen = build_goal_type_screen(self)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def handle_goal_type_selection(self, selected_goal_type):
        self.selected_goal_type = selected_goal_type  # store temporarily
        from snapp.screens.time_span import build_time_span_screen
        self.current_screen = build_time_span_screen(self, selected_goal_type)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def handle_time_frame_selection(self, selected_time_frame, goal_type):
        # Save and move to follow-up
        self.save_data(selected_time_frame, goal_type)
        self.show_followup_screen(selected_time_frame, goal_type)
        self.main_window.show()

    
    def handle_grid_selection(self, x_label, y_label):
        """Save selection immediately and move to follow-up screen."""
        self.save_data(x_label, y_label)  # Save data as soon as a button is clicked
        self.show_followup_screen(x_label, y_label)  # Move to follow-up
        self.main_window.show()

    def show_instructions_screen(self, widget=None):
        self.current_screen = build_instructions_screen(self)
        self.main_window.content = self.current_screen
        self.main_window.show()
               
    def show_followup_screen(self, x_label, y_label, widget=None):
        self.current_screen = build_followup_screen(self, x_label, y_label)
        self.main_window.content = self.current_screen
        self.main_window.show()

    def apply_filter(self, widget):
        """Filter data based on user selection."""
        selected_filter = widget.value

        # Reload full data
        self.load_data()

        if selected_filter != "All":
            self.data = [entry for entry in self.data if entry["time_frame"] == selected_filter]

        self.show_visualization_screen()
    
    def group_entries(self, data, category):
        counts = {}
        for entry in data:
            key = entry.get(category, "Unknown")
            counts[key] = counts.get(key, 0) + 1
        return counts
        
    
    def show_previous_timeframe(self, widget):
        """Go to the previous timeframe and update charts if data exists."""
        previous_date = self.reference_date - self.get_time_offset()
        filtered = self.filter_data_by_timeframe(self.timeframe, reference_date=previous_date)

        if filtered:
            self.reference_date = previous_date
            self.update_chart_only(widget)  
        else:
            print("🚫 No data for previous timeframe.")

    def show_next_timeframe(self, widget):
        """Go to the next timeframe and update charts if data exists."""
        next_date = self.reference_date + self.get_time_offset()
        filtered = self.filter_data_by_timeframe(self.timeframe, reference_date=next_date)

        if filtered:
            self.reference_date = next_date
            self.update_chart_only(widget)  
        else:
            print("🚫 No data for next timeframe.")


    def get_time_offset(self):
        """Return the timedelta offset based on the selected timeframe."""
        if self.timeframe_dropdown.value == "Daily":
            return timedelta(days=1)
        elif self.timeframe_dropdown.value == "Weekly":
            return timedelta(weeks=1)
        elif self.timeframe_dropdown.value == "Monthly":
            return timedelta(days=30)  # Approximate a month
        elif self.timeframe_dropdown.value == "Yearly":
            return timedelta(days=365)  # Approximate a year
        return timedelta(days=0)  # Default
    

    def show_visualization_screen(self, widget=None):
        if not hasattr(self, 'reference_date'):
            self.reference_date = datetime.now()
        
        self.current_screen = build_visualization_screen(self)
        self.main_window.content = self.current_screen
  

    def generate_activity_chart(self, data, chart_type, category):
        grouped_data = self.group_entries(data, category)

        if chart_type == "Bar":
            from snapp.charts.bar_chart import generate_bar_chart_image
            img = generate_bar_chart_image(grouped_data, category_type="goal" if category == "goal_type" else "time")
        elif chart_type == "Pie":
            from snapp.charts.pie_chart import generate_pie_chart_image
            img = generate_pie_chart_image(grouped_data, category_type="goal" if category == "goal_type" else "time")
        else:
            return toga.Label("Unknown chart type")

        filename = f"chart_{uuid.uuid4().hex}.png"
        temp_path = os.path.join(os.path.dirname(__file__), filename)
        img.save(temp_path)

        return Image(temp_path)


      
    def filter_data_by_timeframe(self, timeframe, reference_date=None):
        print(f"🌀 filter_data_by_timeframe() called with timeframe={timeframe}, ref={reference_date}")

        """Filter data based on selected timeframe."""
        if not reference_date:
            reference_date = datetime.now()

        filtered_data = []

        for entry in self.data:
            # ✅ Skip entries without a timestamp to avoid KeyError
            if "timestamp" not in entry or not entry["timestamp"]:
                print("⚠️ Skipping entry without timestamp:", entry)
                continue
            
            try:
                entry_date = datetime.fromisoformat(entry["timestamp"])
            except ValueError:
                print("⚠️ Invalid timestamp format:", entry["timestamp"])
                continue

            # ✅ Debug print to verify filtering logic
            print(f"⏰ Entry Date: {entry_date}, Timeframe: {timeframe}")

            if timeframe == "Daily":
                if entry_date.date() == reference_date.date():
                    filtered_data.append(entry)
            elif timeframe == "Weekly":
                start_of_week = reference_date - timedelta(days=reference_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                if start_of_week.date() <= entry_date.date() <= end_of_week.date():
                    filtered_data.append(entry)
            elif timeframe == "Monthly":
                if (entry_date.year == reference_date.year) and (entry_date.month == reference_date.month):
                    filtered_data.append(entry)
            elif timeframe == "Yearly":
                if entry_date.year == reference_date.year:
                    filtered_data.append(entry)

        # ✅ Move return outside the loop to collect all matching entries
        print(f"✅ Filtered Data ({timeframe}):", filtered_data)
        print(f"🧭 Using reference_date: {reference_date}")
        return filtered_data


    def update_chart_from_dropdown(self, widget):
        """Called when user selects a new timeframe or chart type from dropdowns."""
        import traceback
        print("🔁 update_chart_from_dropdown triggered!")
        traceback.print_stack(limit=5)
        print("🎯 Current timeframe:", self.timeframe_dropdown.value)
        print("🎨 Current chart type:", self.chart_type_dropdown.value)

        # Load fresh data + reset reference date to latest
        self.load_data()
        self.reset_reference_to_latest()

        # Update state
        self.timeframe = self.timeframe_dropdown.value
        self.chart_type = self.chart_type_dropdown.value

        # Now update the chart UI
        self.update_chart_only(widget)

    def update_chart_only(self, widget):
        """Refresh chart display based on existing reference_date and dropdowns."""
        from toga import ImageView
        from toga.style import Pack
        
        if not hasattr(self, "chart_type_dropdown") or not hasattr(self, "timeframe_dropdown"):
            print("⚠️ Dropdowns not initialized yet.")
            return

        print("🧭 Using reference_date (final):", self.reference_date)

        # Filter data based on selected timeframe and current reference date
        filtered_data = self.filter_data_by_timeframe(self.timeframe, reference_date=self.reference_date)

        # Clear old charts
        self.chart_container.children.clear()

        if not filtered_data:
            self.chart_container.add(
                toga.Label("No entries found. Please select a previous time frame.",
                           style=Pack(font_size=14, text_align="center", padding=20))
            )
            return

        #   Generate chart images
        goal_chart = self.generate_activity_chart(filtered_data, self.chart_type, "goal_type")
        time_chart = self.generate_activity_chart(filtered_data, self.chart_type, "time_frame")

        # Add ImageViews
        self.goal_chart_widget = ImageView(goal_chart, style=Pack(width=300, height=300, padding=5))
        self.time_chart_widget = ImageView(time_chart, style=Pack(width=300, height=300, padding=5))

        self.chart_container.add(toga.Label("🎯 Goal-Type Breakdown", style=Pack(font_size=16, padding_bottom=5, padding_top=10)))
        self.chart_container.add(self.goal_chart_widget)
        self.chart_container.add(toga.Label("⏳ Time-Span Breakdown", style=Pack(font_size=16, padding_bottom=5, padding_top=10)))
        self.chart_container.add(self.time_chart_widget)

        # Handle nav button states
        prev_date = self.reference_date - self.get_time_offset()
        next_date = self.reference_date + self.get_time_offset()

        has_prev = any(self.filter_data_by_timeframe(self.timeframe, reference_date=prev_date))
        has_next = any(self.filter_data_by_timeframe(self.timeframe, reference_date=next_date))

        self.prev_button.enabled = has_prev
        self.next_button.enabled = has_next

        print("📊 Goal Chart Grouped:", self.group_entries(filtered_data, "goal_type"))
        print("📊 Time Chart Grouped:", self.group_entries(filtered_data, "time_frame"))

            
    def reset_reference_to_latest(self):
        """Set reference_date to the most recent timestamp in self.data."""
        if not self.data:
            self.reference_date = datetime.now()
            return

        try:
            # Get the latest timestamp from all entries
            latest_entry = max(
                self.data,
                key=lambda x: datetime.fromisoformat(x["timestamp"]) if x.get("timestamp") else datetime.min
            )
            self.reference_date = datetime.fromisoformat(latest_entry["timestamp"])
            print(f"📌 Reference date set to latest entry: {self.reference_date}")
        except Exception as e:
            print("⚠️ Could not determine latest reference date:", e)
            self.reference_date = datetime.now()
    
    def after_login_success(self, id_token):
        print("🚀 after_login_success called!")  # Optional debug
        self.user_token = id_token
        from snapp.services.local_db import setup_local_database
        self.conn, self.cursor = setup_local_database(self)
        self.load_data()
        self.sync_offline_data()
        self.show_instructions_screen()

def main():
    return ActivityLogger()

if __name__ == "__main__":
    main().main_loop()
