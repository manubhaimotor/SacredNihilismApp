import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, LEFT
from snapp.utils.ui_helpers import get_settings_footer, get_header_nav

def build_instructions_screen(app):
    instructions_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=CENTER))

    # 🧭 Global header nav (← / →)
    if getattr(app, "has_logged_in", False):
        instructions_box.add(get_header_nav(app))

    # 📝 Instructions Text
    instructions_box.add(toga.Label("Instructions for use:", style=Pack(font_size=20, font_weight="bold", text_align=LEFT, padding=(5, 0))))
    instructions_box.add(toga.Label("1. Take 5 seconds to observe your actions.", style=Pack(font_size=18, text_align=LEFT, padding=(5, 0))))
    instructions_box.add(toga.Label("2. What goal are you working towards?", style=Pack(font_size=18, text_align=LEFT, padding=(5, 0))))
    instructions_box.add(toga.Label("3. Press the button once you're ready.", style=Pack(font_size=18, text_align=LEFT, padding=(5, 0))))

    # ✅ Proceed
    instructions_box.add(toga.Button(
        "Proceed",
        on_press=app.show_goal_type_screen,
        style=Pack(font_size=16, padding=10, background_color="#a12766", color="white")
    ))

    # ⚙️ Footer with dual access (Settings + Track Data)
    instructions_box.add(get_settings_footer(app, back_action=app.show_instructions_screen))

    return toga.ScrollContainer(content=instructions_box)
