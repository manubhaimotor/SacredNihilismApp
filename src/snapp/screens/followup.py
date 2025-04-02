import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, CENTER

def build_followup_screen(app, x_label, y_label):
    """Step 3: Display the follow-up screen with enhanced layout and text formatting."""
    followup_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # Back Button
    back_button = toga.Button(
        "←",
        on_press=app.show_goal_type_screen,
        style=Pack(width=50, font_size=12, padding=5, alignment=LEFT)
    )
    followup_box.add(back_button)

    # "Your Choice" section
    followup_box.add(toga.Label("Your Choice:", style=Pack(font_size=18, font_weight="bold", padding=(5, 0))))
    followup_box.add(toga.Label(f"Goal Type: {y_label}", style=Pack(font_size=16, padding=(5, 0))))
    followup_box.add(toga.Label(f"Time Frame: {x_label}", style=Pack(font_size=16, padding=(5, 0))))

    followup_box.add(toga.Label("For this goal type and time frame, ask:", style=Pack(font_size=16, padding=(10, 0))))
    followup_box.add(toga.Label("What else is there to do?", style=Pack(font_size=20, font_weight="bold", padding=(5, 0))))

    # Track Data Button
    track_data_button = toga.Button(
        "Track Your Data",
        on_press=app.show_visualization_screen,
        style=Pack(font_size=16, padding=10, background_color="#a12766", color="white")
    )
    followup_box.add(track_data_button)

    # Legend
    legend_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))
    legend_box.add(toga.Label("Legend:", style=Pack(font_size=10, font_weight="bold", padding=(5, 0))))

    legend_data = [
        ("Physical", "Will result in improved physical sensations", "Immediate Term", "Now to a few weeks"),
        ("Biological", "Will either strengthen identitiy, improve control or increase access to resources", "Short Term", "Few weeks to 18 months"),
        ("Biology+", "You cannot imagine what the end goal would be", "Long Term", "18 months and beyond")
    ]

    for goal_type, goal_def, time_type, time_def in legend_data:
        row = toga.Box(style=Pack(direction=ROW, alignment=LEFT, padding=(5, 0)))
        row.add(toga.Label(goal_type, style=Pack(font_size=10, width=100, font_weight="bold")))
        row.add(toga.Label(goal_def, style=Pack(font_size=10, width=350, text_align=LEFT, padding=5, height=60)))
        row.add(toga.Label(time_type, style=Pack(font_size=10, width=120, font_weight="bold")))
        row.add(toga.Label(time_def, style=Pack(font_size=10, width=200)))
        legend_box.add(row)

    followup_box.add(legend_box)

    return followup_box
