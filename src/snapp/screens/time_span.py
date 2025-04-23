import toga
from toga.style import Pack
from toga.style.pack import COLUMN, LEFT
from snapp.utils.ui_helpers import get_settings_footer, get_header_nav

def build_time_span_screen(app, selected_goal_type):
    time_span_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # 🧭 Global header nav (← / →)
    if getattr(app, "has_logged_in", False):
        time_span_box.add(get_header_nav(app))

    # 🏷️ Title
    time_span_box.add(toga.Label("Choose your Time Frame", style=Pack(font_size=18, font_weight="bold", padding=(5, 10))))

    # 🔘 Time Frame Buttons
    for time_frame in ["Immediate Term", "Short Term", "Medium Term", "Long Term"]:
        button = toga.Button(
            time_frame,
            on_press=lambda w, t=time_frame: app.handle_time_frame_selection(t, selected_goal_type),
            style=Pack(padding=5, font_size=16, width=220)
        )
        time_span_box.add(button)

    # 🧾 Legend
    legend_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))
    legend_box.add(toga.Label("Legend:", style=Pack(font_size=12, font_weight="bold", padding=(10, 0))))

    time_legend = [
        ("Immediate Term", "Now to a few hours"),
        ("Short Term", "1 day to a few weeks"),
        ("Medium Term", "Few weeks to 18 months"),
        ("Long Term", "18 months and beyond"),
    ]

    for label, desc in time_legend:
        row = toga.Box(style=Pack(direction=COLUMN, padding=5))
        row.add(toga.Label(label, style=Pack(font_size=10, font_weight="bold")))
        row.add(toga.Label(desc, style=Pack(font_size=10, width=400, padding=(0, 10))))
        legend_box.add(row)

    time_span_box.add(legend_box)

    # ⚙️ Dual-footer (Track Your Data + Settings)
    time_span_box.add(get_settings_footer(app, back_action=app.show_time_span_screen))

    return toga.ScrollContainer(content=time_span_box)
