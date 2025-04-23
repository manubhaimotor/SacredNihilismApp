from datetime import datetime, timedelta
from toga import ImageView, Label, Box
from toga.style import Pack
import os, uuid, gc
from toga import Image
from snapp.charts.bar_chart import generate_bar_chart_image
from snapp.charts.pie_chart import generate_pie_chart_image

class ChartController:
    def __init__(self, app):
        self.app = app

    def group_entries(self, data, category):
        counts = {}
        for entry in data:
            key = entry.get(category, "Unknown")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def generate_activity_chart(self, data, chart_type, category):
        grouped = self.group_entries(data, category)
        if chart_type == "Bar":
            img = generate_bar_chart_image(grouped, category_type="goal" if category == "goal_type" else "time")
        elif chart_type == "Pie":
            img = generate_pie_chart_image(grouped, category_type="goal" if category == "goal_type" else "time")
        else:
            return None, None
        filename = f"chart_{uuid.uuid4().hex}.png"
        path = os.path.join(os.path.dirname(__file__), filename)
        img.save(path)
        return Image(path), path

    def get_time_offset(self):
        val = self.app.timeframe_dropdown.value
        return {
            "Daily": timedelta(days=1),
            "Weekly": timedelta(weeks=1),
            "Monthly": timedelta(days=30),
            "Yearly": timedelta(days=365)
        }.get(val, timedelta(days=0))

    def reset_reference_to_latest(self):
        if not self.app.data:
            self.app.reference_date = datetime.now()
            return
        try:
            latest = max(self.app.data, key=lambda x: datetime.fromisoformat(x["timestamp"]) if x.get("timestamp") else datetime.min)
            self.app.reference_date = datetime.fromisoformat(latest["timestamp"])
        except Exception as e:
            print("⚠️ Could not determine latest reference date:", e)
            self.app.reference_date = datetime.now()

    def filter_data_by_timeframe(self, timeframe, reference_date=None):
        if not reference_date:
            reference_date = datetime.now()
        filtered = []
        for entry in self.app.data:
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
        if not hasattr(self.app, "chart_type_dropdown") or not hasattr(self.app, "timeframe_dropdown"):
            print("⚠️ Dropdowns not initialized yet.")
            return

        new_chart_container = Box(style=Pack(direction="column", padding=5))
        self.app.chart_container_parent.remove(self.app.chart_container)
        self.app.chart_container = new_chart_container
        self.app.chart_container_parent.add(self.app.chart_container)

        def format_reference_range():
            date = self.app.reference_date
            if self.app.timeframe == "Daily":
                return f"Data Range: {date.strftime('%m/%d/%Y')} to {date.strftime('%m/%d/%Y')}"
            elif self.app.timeframe == "Weekly":
                start = date - timedelta(days=date.weekday())
                end = start + timedelta(days=6)
                return f"Data Range: {start.strftime('%m/%d/%Y')} to {end.strftime('%m/%d/%Y')}"
            elif self.app.timeframe == "Monthly":
                start = date.replace(day=1)
                end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                return f"Data Range: {start.strftime('%m/%d/%Y')} to {end.strftime('%m/%d/%Y')}"
            elif self.app.timeframe == "Yearly":
                start = date.replace(month=1, day=1)
                end = date.replace(month=12, day=31)
                return f"Data Range: {start.strftime('%m/%d/%Y')} to {end.strftime('%m/%d/%Y')}"
            return "Data Range: Unknown"

        self.app.chart_container.add(Label(format_reference_range(), style=Pack(font_size=14, padding=(5, 5, 10, 5))))
        filtered = self.filter_data_by_timeframe(self.app.timeframe, self.app.reference_date)

        if hasattr(self.app, "last_chart_file_path") and self.app.last_chart_file_path:
            try:
                gc.collect()
                os.remove(self.app.last_chart_file_path)
            except Exception as e:
                print("⚠️ Could not delete old chart file:", e)

        if not filtered:
            self.app.chart_container.add(Label("No data for this time period.", style=Pack(font_size=14, padding=10)))
        else:
            goal_chart, path = self.generate_activity_chart(filtered, self.app.chart_type, "goal_type")
            time_chart, _ = self.generate_activity_chart(filtered, self.app.chart_type, "time_frame")
            self.app.last_chart_file_path = path

            self.app.goal_chart_widget = ImageView(goal_chart, style=Pack(width=300, height=300, padding=5))
            self.app.time_chart_widget = ImageView(time_chart, style=Pack(width=300, height=300, padding=5))

            self.app.chart_container.add(Label("🎯 Goal-Type Breakdown", style=Pack(font_size=16, padding_bottom=5, padding_top=10)))
            self.app.chart_container.add(self.app.goal_chart_widget)
            self.app.chart_container.add(Label("⏳ Time-Span Breakdown", style=Pack(font_size=16, padding_bottom=5, padding_top=10)))
            self.app.chart_container.add(self.app.time_chart_widget)

        self.app.prev_button.enabled = any(datetime.fromisoformat(e["timestamp"]) < self.app.reference_date for e in self.app.data if "timestamp" in e)
        self.app.next_button.enabled = any(datetime.fromisoformat(e["timestamp"]) > self.app.reference_date for e in self.app.data if "timestamp" in e)

    def show_previous_timeframe(self, widget):
        offset = self.get_time_offset()
        current = self.app.reference_date
        earliest = min((datetime.fromisoformat(e["timestamp"]) for e in self.app.data if "timestamp" in e), default=datetime.min)

        while current > earliest:
            current -= offset
            filtered = self.filter_data_by_timeframe(self.app.timeframe, current)
            if filtered:
                self.app.reference_date = current
                self.update_chart_only(widget)
                return
        self.app.prev_button.enabled = False
        self.update_chart_only(widget)

    def show_next_timeframe(self, widget):
        offset = self.get_time_offset()
        current = self.app.reference_date
        latest = max((datetime.fromisoformat(e["timestamp"]) for e in self.app.data if "timestamp" in e), default=datetime.max)

        while current < latest:
            current += offset
            filtered = self.filter_data_by_timeframe(self.app.timeframe, current)
            if filtered:
                self.app.reference_date = current
                self.update_chart_only(widget)
                return
        self.app.next_button.enabled = False
        self.update_chart_only(widget)

    def update_chart_from_dropdown(self, widget):
        if not hasattr(self.app, "chart_type_dropdown") or not hasattr(self.app, "timeframe_dropdown"):
            print("⚠️ Dropdowns not initialized yet.")
            return
        self.app.load_data()
        self.reset_reference_to_latest()
        self.app.timeframe = self.app.timeframe_dropdown.value
        self.app.chart_type = self.app.chart_type_dropdown.value
        self.update_chart_only(widget)

