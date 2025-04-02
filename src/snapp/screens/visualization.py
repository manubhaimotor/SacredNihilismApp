import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, CENTER

def build_visualization_screen(app):
    """Display tracking screen with two charts and filters."""
    vis_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # Back Button
    back_button = toga.Button(
        "←", on_press=app.show_instructions_screen,
        style=Pack(width=50, font_size=12, padding=5, alignment=LEFT)
    )
    vis_box.add(back_button)

    vis_box.add(toga.Label("Track Your Life", style=Pack(font_size=20, font_weight="bold", padding=10)))

    # Load Data
    app.load_data()

    # Time Filter Dropdown
    app.timeframe_dropdown = toga.Selection(
        items=["Daily", "Weekly", "Monthly", "Yearly"],
        on_select=app.update_chart_based_on_filter,
        style=Pack(padding=10)
    )
    app.timeframe_dropdown.value = "Monthly"
    vis_box.add(toga.Label("Select Timeframe:", style=Pack(padding=5)))
    vis_box.add(app.timeframe_dropdown)

    # Chart Type Dropdown
    app.chart_type_dropdown = toga.Selection(
        items=["Bar", "Pie"],
        on_select=app.update_chart_based_on_filter,
        style=Pack(padding=10)
    )
    app.chart_type_dropdown.value = "Bar"
    vis_box.add(toga.Label("Select Chart Type:", style=Pack(padding=5)))
    vis_box.add(app.chart_type_dropdown)

    # Navigation buttons
    nav_box = toga.Box(style=Pack(direction=ROW, padding=10, alignment=CENTER))
    app.prev_button = toga.Button(
        "← Previous",
        on_press=app.show_previous_timeframe,
        style=Pack(font_size=14, padding=10)
    )
    app.next_button = toga.Button(
        "Next →",
        on_press=app.show_next_timeframe,
        style=Pack(font_size=14, padding=10)
    )
    nav_box.add(app.prev_button)
    nav_box.add(app.next_button)
    vis_box.add(nav_box)

    # Filtered Data
    filtered_data = app.filter_data_by_timeframe(app.timeframe_dropdown.value)

    if not filtered_data:
        vis_box.add(toga.Label("No entries found. Please select a previous time frame.",
                               style=Pack(font_size=14, text_align=CENTER, padding=20)))
    else:
        goal_chart = app.generate_activity_chart(filtered_data, app.chart_type_dropdown.value, "goal_type")
        time_chart = app.generate_activity_chart(filtered_data, app.chart_type_dropdown.value, "time_frame")

        charts_box = toga.Box(style=Pack(direction=ROW, padding=10, alignment=CENTER))
        app.goal_chart_widget = toga.ImageView(goal_chart, style=Pack(width=300, height=300, padding=5))
        app.time_chart_widget = toga.ImageView(time_chart, style=Pack(width=300, height=300, padding=5))
        charts_box.add(app.goal_chart_widget)
        charts_box.add(app.time_chart_widget)
        vis_box.add(charts_box)

    return vis_box
