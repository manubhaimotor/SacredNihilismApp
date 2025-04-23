import toga
from toga.style import Pack
from toga.style.pack import ROW, CENTER, RIGHT


import toga
from toga.style import Pack
from toga.style.pack import ROW, RIGHT

def get_settings_footer(app, back_action):
    footer_box = toga.Box(style=Pack(direction=ROW, padding_top=20, padding_bottom=10, alignment=RIGHT))

    # 🏠 Home Button → Instructions screen
    home_btn = toga.Button(
        "Home",
        on_press=lambda w: app.show_instructions_screen(),
        style=Pack(padding=10)
    )

    # 📊 Track Your Data → Visualization screen
    track_data_btn = toga.Button(
        "Track Your Data",
        on_press=lambda w: app.show_visualization_screen(),
        style=Pack(padding=10)
    )

    # ⚙️ Settings → Settings screen with return action
    settings_btn = toga.Button(
        "Settings",
        on_press=lambda w: app.show_settings_screen(back_action=back_action),
        style=Pack(padding=10)
    )

    footer_box.add(home_btn)
    footer_box.add(track_data_btn)
    footer_box.add(settings_btn)

    return footer_box



def get_header_nav(app):
    nav_box = toga.Box(style=Pack(direction=ROW, padding=10, alignment=RIGHT))

    back_button = toga.Button("←", on_press=app.go_back, style=Pack(width=40, padding_right=5))
    forward_button = toga.Button("→", on_press=app.go_forward, style=Pack(width=40))

    # Dynamically enable/disable based on history state
    back_button.enabled = bool(getattr(app, "screen_history", []))
    forward_button.enabled = bool(getattr(app, "forward_stack", []))

    nav_box.add(back_button)
    nav_box.add(forward_button)

    return nav_box

