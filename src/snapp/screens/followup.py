import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT
from datetime import datetime
from snapp.utils.ui_helpers import get_settings_footer, get_header_nav
from snapp.services.nudge_scheduler import generate_nudge_times
from snapp.services.local_db import get_meta_value, set_meta_value

def build_followup_screen(app, x_label, y_label):
    followup_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # 🧭 Global header nav (← / →)
    if getattr(app, "has_logged_in", False):
        followup_box.add(get_header_nav(app))

    # 🔔 One-time daily nudge scheduling
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_scheduled = get_meta_value(app.conn, "last_nudge_schedule_date")

    if last_scheduled != today_str:
        nudges = app.nudge_settings.get("nudges_per_day", 4)
        start_hour = app.nudge_settings.get("start_hour", 9)
        end_hour = app.nudge_settings.get("end_hour", 21)
        strategy = app.nudge_settings.get("strategy", "evenly")

        generate_nudge_times(nudges, start_hour, end_hour, strategy)
        set_meta_value(app.conn, "last_nudge_schedule_date", today_str)
        print("✅ Nudge schedule saved for today.")
    else:
        print("🕒 Nudges already scheduled today (persisted).")

    # 🎯 User choice summary
    followup_box.add(toga.Label("Your Choice:", style=Pack(font_size=14, font_weight="bold", padding=(5, 0))))
    followup_box.add(toga.Label(f"Goal Type: {y_label}", style=Pack(font_size=12, padding=(5, 0))))

    goal_descriptions = {
        "Physical": "Will result in improved physical sensations",
        "Biological": "Will either strengthen identity, improve control or increase access to resources",
        "Beyond Biology": "You cannot imagine what the end goal would be"
    }
    if y_label in goal_descriptions:
        followup_box.add(toga.Label(goal_descriptions[y_label], style=Pack(font_size=10, color="#444444", padding=(0, 0))))

    followup_box.add(toga.Label(f"Time Frame: {x_label}", style=Pack(font_size=12, padding=(10, 0))))

    time_descriptions = {
        "Immediate Term": "Now to a few weeks",
        "Short Term": "Few weeks to 18 months",
        "Long Term": "18 months and beyond"
    }
    if x_label in time_descriptions:
        followup_box.add(toga.Label(time_descriptions[x_label], style=Pack(font_size=10, color="#444444", padding=(0, 5))))

    followup_box.add(toga.Label("For this goal type and time frame, ask:", style=Pack(font_size=12, padding=(10, 5))))
    followup_box.add(toga.Label("What else is there to do?", style=Pack(font_size=24, font_weight="bold", padding=(5, 0))))

    # ⚙️ Footer with global access to settings and visualization
    followup_box.add(get_settings_footer(app, back_action=lambda w: app.show_followup_screen(app.last_x_label, app.last_y_label)))

    return toga.ScrollContainer(content=followup_box)
