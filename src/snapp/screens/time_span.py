import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, LEFT

def build_time_span_screen(app, selected_goal_type):
    time_span_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # Title
    time_span_box.add(toga.Label("Choose your Time Frame", style=Pack(font_size=18, font_weight="bold", padding=(5, 10))))

    # Time Frame Buttons (Vertical)
    time_frames = [
        "Immediate Term",
        "Short Term",
        "Medium Term",
        "Long Term"
    ]

    for time_frame in time_frames:
        button = toga.Button(
            time_frame,
            on_press=lambda w, t=time_frame: app.handle_time_frame_selection(t, selected_goal_type),
            style=Pack(padding=5, font_size=16, width=220)
        )
        time_span_box.add(button)

    # Legend
    legend_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))
    legend_box.add(toga.Label("Legend:", style=Pack(font_size=12, font_weight="bold", padding=(10, 0))))

    time_legend = [
        ("Immediate Term", "Now to a few hours"),
        ("Short Term", "1 day to a few weeks"),
        ("Medium Term", "Few weeks to 18 months"),
        ("Long Term", "18 months and beyond"),
    ]

    for label, desc in time_legend:
        legend_row = toga.Box(style=Pack(direction=COLUMN, padding=5))
        legend_row.add(toga.Label(label, style=Pack(font_size=10, font_weight="bold")))
        legend_row.add(toga.Label(desc, style=Pack(font_size=10, width=400, padding=(0, 10))))
        legend_box.add(legend_row)

    time_span_box.add(legend_box)

    # Back Button
    back_button = toga.Button(
        "← Back",
        on_press=app.show_goal_type_screen,
        style=Pack(padding=10, font_size=12)
    )
    time_span_box.add(back_button)

    return time_span_box
