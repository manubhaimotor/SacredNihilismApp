import toga
from toga import Button, Label, Box, Selection, ScrollContainer
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, CENTER
from snapp.utils.ui_helpers import get_settings_footer, get_header_nav

def build_visualization_screen(app):
    vis_box = Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # 🧭 Global header nav (← / →)
    if getattr(app, "has_logged_in", False):
        vis_box.add(get_header_nav(app))

    # 🏷️ Title
    vis_box.add(Label("Track Your Life", style=Pack(font_size=20, font_weight="bold", text_align=CENTER, padding_bottom=10)))

    # 📅 Data + state setup
    app.load_data()
    app.reset_reference_to_latest()
    app.timeframe = getattr(app, "timeframe", "Monthly")
    app.chart_type = getattr(app, "chart_type", "Bar")

    # 📅 Timeframe dropdown
    vis_box.add(Label("Select Timeframe:", style=Pack(padding=5)))
    app.timeframe_dropdown = Selection(
        items=["Daily", "Weekly", "Monthly", "Yearly"],
        on_select=app.update_chart_from_dropdown,
        style=Pack(padding=10)
    )
    app.timeframe_dropdown.value = app.timeframe
    vis_box.add(app.timeframe_dropdown)

    # 📊 Chart type dropdown
    vis_box.add(Label("Select Chart Type:", style=Pack(padding=5)))
    app.chart_type_dropdown = Selection(
        items=["Bar", "Pie"],
        on_select=app.update_chart_from_dropdown,
        style=Pack(padding=10)
    )
    app.chart_type_dropdown.value = app.chart_type
    vis_box.add(app.chart_type_dropdown)

    # ⬅️➡️ Local timeframe nav
    data_nav = Box(style=Pack(direction=ROW, padding_top=5, padding_bottom=10, alignment=CENTER))
    app.prev_button = Button("← Previous", on_press=app.show_previous_timeframe, style=Pack(padding=10, font_size=14))
    app.next_button = Button("Next →", on_press=app.show_next_timeframe, style=Pack(padding=10, font_size=14))
    data_nav.add(app.prev_button)
    data_nav.add(app.next_button)
    vis_box.add(data_nav)

    # 📊 Chart container
    app.chart_container = Box(style=Pack(direction=COLUMN, padding=5))
    app.chart_container_parent = Box(style=Pack(direction=COLUMN))
    app.chart_container_parent.add(app.chart_container)
    vis_box.add(app.chart_container_parent)

    # ⚙️ Global footer (Settings + "Track your data")
    vis_box.add(get_settings_footer(app, back_action=app.show_visualization_screen))

    # 🧭 Chart render
    app.update_chart_only(widget=None)

    return ScrollContainer(content=vis_box)
