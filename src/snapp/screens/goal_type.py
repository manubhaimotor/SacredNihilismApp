import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, LEFT

def build_goal_type_screen(app):
    goal_type_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))

    # Title
    goal_type_box.add(toga.Label("Choose your Goal Type", style=Pack(font_size=18, font_weight="bold", padding=(5, 10))))

    # Goal Type Buttons (Vertical Layout)
    for goal_type in ["Physical", "Biological", "Biology+"]:
        button = toga.Button(
            goal_type,
            on_press=lambda w, g=goal_type: app.handle_goal_type_selection(g),
            style=Pack(padding=5, font_size=16, width=200)
        )
        goal_type_box.add(button)

    # Legend
    legend_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=LEFT))
    legend_box.add(toga.Label("Legend:", style=Pack(font_size=12, font_weight="bold", padding=(10, 0))))

    goal_type_legend = [
        ("Physical", "Will result in improved physical sensations"),
        ("Biological", "Will strengthen identity, improve control, or increase access to resources"),
        ("Biology+", "You cannot imagine what the end goal would be"),
    ]

    for label, desc in goal_type_legend:
        legend_row = toga.Box(style=Pack(direction=COLUMN, padding=5))
        legend_row.add(toga.Label(label, style=Pack(font_size=10, font_weight="bold")))
        legend_row.add(toga.Label(desc, style=Pack(font_size=10, width=400, padding=(0, 10))))
        legend_box.add(legend_row)

    goal_type_box.add(legend_box)

    # Back Button
    back_button = toga.Button(
        "← Back",
        on_press=app.show_instructions_screen,
        style=Pack(padding=10, font_size=12)
    )
    goal_type_box.add(back_button)

    return toga.ScrollContainer(content=goal_type_box)

    
