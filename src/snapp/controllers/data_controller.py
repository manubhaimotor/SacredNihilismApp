from snapp.services.local_db import insert_entry, get_all_entries, get_unsynced_entries, mark_entry_as_synced
from snapp.services.firestore_sync import upload_to_firestore, fetch_from_firestore
from snapp.utils.net_utils import is_online
from datetime import datetime

class DataController:
    def __init__(self, app):
        self.app = app

    def save_data(self, x_label, y_label, note=None):
        timestamp = datetime.now().isoformat()
        entry = {
            "goal_type": y_label,
            "time_frame": x_label,
            "note": note or "",
            "timestamp": timestamp
        }
        try:
            insert_entry(self.app.cursor, self.app.conn, entry)
            if is_online() and self.app.user_token:
                if upload_to_firestore(self.app.user_token, entry):
                    mark_entry_as_synced(self.app.cursor, self.app.conn, timestamp)
        except Exception as e:
            print("❌ Error saving data:", e)

    def load_data(self):
        if not hasattr(self.app, "cursor") or self.app.cursor is None:
            print("⚠️ Cannot load data — SQLite cursor not initialized yet.")
            self.app.data = []
            return
        try:
            self.app.data = get_all_entries(self.app.cursor)
            if is_online() and self.app.user_token:
                firestore_entries = fetch_from_firestore(self.app.user_token)
                existing_ts = {entry["timestamp"] for entry in self.app.data if entry.get("timestamp")}
                new_entries = [e for e in firestore_entries if e.get("timestamp") not in existing_ts]
                self.app.data.extend(new_entries)
        except Exception as e:
            print("⚠️ Failed to load data:", e)
            self.app.data = []

    def sync_offline_data(self):
        if not is_online() or not self.app.user_token:
            print("⚠️ Cannot sync data. Offline or missing token.")
            return
        for entry in get_unsynced_entries(self.app.cursor):
            entry_id, goal_type, time_frame, note, timestamp = entry
            try:
                if upload_to_firestore(self.app.user_token, {
                    "goal_type": goal_type,
                    "time_frame": time_frame,
                    "note": note,
                    "timestamp": timestamp
                }):
                    mark_entry_as_synced(self.app.cursor, self.app.conn, entry_id)
            except Exception as e:
                print(f"❌ Error syncing entry {entry_id}: {e}")

    def handle_time_frame_selection(self, selected_time_frame, goal_type):
        self.save_data(selected_time_frame, goal_type)
        self.app.navigation.show_followup_screen(selected_time_frame, goal_type)

    def handle_goal_type_selection(self, selected_goal_type):
        self.app.selected_goal_type = selected_goal_type
        self.app.navigation.show_time_span_screen(selected_goal_type)
