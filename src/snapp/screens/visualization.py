import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, CENTER
from snapp.utils.ui_helpers import get_settings_footer

def build_visualization_screen(app):
    from toga.style import Pack
    from toga.style.pack import COLUMN, ROW, LEFT, CENTER
    from snapp.utils.ui_helpers import get_settings_footer

    vis_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    vis_box.add(toga.Button("←", on_press=app.show_instructions_screen,
                            style=Pack(width=50, font_size=12, padding=5, alignment=LEFT)))
    vis_box.add(toga.Label("Track Your Life", style=Pack(font_size=20, font_weight="bold", padding=10)))

    app.load_data()

    vis_box.add(toga.Label("Select Timeframe:", style=Pack(padding=5)))
    app.timeframe_dropdown = toga.Selection(
        items=["Daily", "Weekly", "Monthly", "Yearly"],
        on_select=app.update_chart_from_dropdown,
        style=Pack(padding=10)
    )
    app.timeframe_dropdown.value = getattr(app, "timeframe", "Monthly")
    vis_box.add(app.timeframe_dropdown)

    vis_box.add(toga.Label("Select Chart Type:", style=Pack(padding=5)))
    app.chart_type_dropdown = toga.Selection(
        items=["Bar", "Pie"],
        on_select=app.update_chart_from_dropdown,
        style=Pack(padding=10)
    )
    app.chart_type_dropdown.value = getattr(app, "chart_type", "Bar")
    vis_box.add(app.chart_type_dropdown)

    nav_box = toga.Box(style=Pack(direction=ROW, padding=10, alignment=CENTER))
    app.prev_button = toga.Button("← Previous", on_press=app.show_previous_timeframe, style=Pack(font_size=14, padding=10))
    app.next_button = toga.Button("Next →", on_press=app.show_next_timeframe, style=Pack(font_size=14, padding=10))
    nav_box.add(app.prev_button)
    nav_box.add(app.next_button)
    vis_box.add(nav_box)

    # 🔁 Wrap chart container for safe replacement
    app.chart_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
    app.chart_container_parent = toga.Box(style=Pack(direction=COLUMN))
    app.chart_container_parent.add(app.chart_container)
    vis_box.add(app.chart_container_parent)

    vis_box.add(get_settings_footer(app, back_action=app.show_visualization_screen))

    app.reset_reference_to_latest()
    app.timeframe = app.timeframe_dropdown.value
    app.chart_type = app.chart_type_dropdown.value
    app.update_chart_only(widget=None)

    return toga.ScrollContainer(content=vis_box)
