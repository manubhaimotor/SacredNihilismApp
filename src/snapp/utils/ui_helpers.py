import toga
from toga.style import Pack

def get_settings_footer(app, back_action):
    footer_box = toga.Box(style=Pack(direction='row', padding_top=20, padding_bottom=10))
    settings_btn = toga.Button(
        "Settings",
        on_press=lambda w: app.show_settings_screen(back_action=back_action),
        style=Pack(padding=10)
    )
    footer_box.add(settings_btn)
    return footer_box

