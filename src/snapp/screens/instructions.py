import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, LEFT

def build_instructions_screen(app):
    """Step 1: Display the instructions screen with Proceed and Track Data buttons."""
    instructions_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=CENTER))

    # Instructions
    instructions_box.add(toga.Label("Instructions for use:", style=Pack(font_size=20, font_weight="bold", text_align=LEFT, padding=(5, 0))))
    instructions_box.add(toga.Label("1. Take 5 seconds to observe your actions.", style=Pack(font_size=18, text_align=LEFT, padding=(5, 0))))
    instructions_box.add(toga.Label("2. What goal are you working towards?", style=Pack(font_size=18, text_align=LEFT, padding=(5, 0))))
    instructions_box.add(toga.Label("3. Press the button once you're ready.", style=Pack(font_size=18, text_align=LEFT, padding=(5, 0))))

    # Proceed Button
    proceed_button = toga.Button(
        "Proceed",
        on_press=app.show_goal_type_screen,
        style=Pack(font_size=16, padding=10, background_color="#a12766", color="white")
    )
    instructions_box.add(proceed_button)

    # Track Data Button
    track_data_button = toga.Button(
        "Track Your Data",
        on_press=app.show_visualization_screen,
        style=Pack(font_size=16, padding=10)
    )
    instructions_box.add(track_data_button)

    return toga.ScrollContainer(content=instructions_box)
    
