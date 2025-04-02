import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, CENTER, RIGHT

def build_grid_screen(app):
    """Step 2: Display the categorization grid."""
    x_labels = ["Immediate Term", "Short Term", "Long Term"]
    y_labels = ["Physical", "Biological", "Biology+"]
    label_width = 120
    cell_width = 160

    grid_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # Back Button (Left-Aligned)
    back_button = toga.Button(
        "←",
        on_press=app.show_instructions_screen,
        style=Pack(width=50, font_size=12, padding=5, alignment=LEFT)
    )
    grid_box.add(back_button)

    # Screen Title
    grid_box.add(toga.Label("Categorize your goal into the grid below.", style=Pack(font_size=18, font_weight="bold", padding=10)))

    # X-axis label row with Time Span title
    x_axis_label_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding=(10, label_width)))
    x_axis_label_box.add(toga.Label("Time Span", style=Pack(font_size=16, font_weight="bold", font_style="italic", text_align=CENTER, padding=(0, label_width))))
    x_axis_label_box.add(toga.Label("→", style=Pack(font_size=20, text_align=RIGHT, padding=(0, 10))))
    grid_box.add(x_axis_label_box)

    # X-axis header row for grid
    x_label_box = toga.Box(style=Pack(direction=ROW, padding=(0, 0, 10, label_width), alignment=CENTER))
    x_label_box.add(toga.Label(" ", style=Pack(width=label_width)))  # Left-padding spacer
    for x_label in x_labels:
        x_label_box.add(toga.Label(x_label, style=Pack(width=cell_width, padding=5, text_align=CENTER, font_size=14, font_style="italic")))
    grid_box.add(x_label_box)

    # Y-axis label box
    y_axis_label_box = toga.Box(style=Pack(direction=COLUMN, alignment=LEFT))
    y_axis_label_box.add(toga.Label("↑", style=Pack(font_size=20, text_align=CENTER)))
    y_axis_label_box.add(toga.Label("Goal Type", style=Pack(font_size=16, font_weight="bold", font_style="italic", text_align=CENTER)))
    y_axis_label_box.add(toga.Label("↓", style=Pack(font_size=20, text_align=CENTER)))

    # Container for grid rows
    grid_container = toga.Box(style=Pack(direction=ROW, alignment=LEFT))
    grid_container.add(y_axis_label_box)

    rows_box = toga.Box(style=Pack(direction=COLUMN, alignment=LEFT))
    for y_label in y_labels:
        row_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        row_box.add(toga.Label(
            y_label,
            style=Pack(width=label_width, padding=5, font_size=14, font_style="italic", text_align=RIGHT)
        ))
        for x_label in x_labels:
            row_box.add(toga.Button(
                "",
                on_press=lambda w, x=x_label, y=y_label: app.handle_grid_selection(x, y),
                style=Pack(width=cell_width, padding=5, font_size=14)
            ))
        rows_box.add(row_box)
    grid_container.add(rows_box)
    grid_box.add(grid_container)

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

    grid_box.add(legend_box)

    return grid_box
