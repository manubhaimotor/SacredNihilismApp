import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT
from snapp.services.settings_sync import save_settings_to_firestore, load_settings_from_firestore
from snapp.services.local_db import set_meta_value  # ✅ Still needed to clear the cache on save


def build_settings_screen(app, back_action=None):
    main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=LEFT))

    # 🔁 Load from Firebase if not already fetched
    if not getattr(app, "nudge_settings", None):
        try:
            app.nudge_settings = load_settings_from_firestore(app.user_token, app.user_id)
            print("🧠 Refetched settings in settings screen:", app.nudge_settings)
        except Exception as e:
            print("⚠️ Error refetching settings in settings screen:", e)
            app.nudge_settings = {}

    settings = app.nudge_settings or {}

    # 🔙 Back Button
    if back_action:
        back_btn = toga.Button("← Back", on_press=back_action, style=Pack(padding_bottom=10))
        main_box.add(back_btn)

    # --- 🔔 Nudge Settings ---
    main_box.add(toga.Label("🔔 Nudge Settings", style=Pack(font_size=18, font_weight="bold", padding=(10, 0, 5, 0))))

    main_box.add(toga.Label("Number of nudges per day:"))
    app.nudges_input = toga.TextInput(
        value=str(settings.get("nudges_per_day", "3")),
        placeholder="e.g., 3",
        style=Pack(padding_bottom=10)
    )
    main_box.add(app.nudges_input)

    main_box.add(toga.Label("Hours of operation (Start to End):"))
    hour_options = [f"{i} AM" for i in range(1, 13)] + [f"{i} PM" for i in range(1, 13)]
    hours_row = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
    app.start_hour = toga.Selection(
        items=hour_options,
        value=settings.get("hours_start", "9 AM"),
        style=Pack(padding_right=10)
    )
    app.end_hour = toga.Selection(
        items=hour_options,
        value=settings.get("hours_end", "9 PM")
    )
    hours_row.add(app.start_hour)
    hours_row.add(toga.Label("to", style=Pack(padding_left=5, padding_right=5)))
    hours_row.add(app.end_hour)
    main_box.add(hours_row)

    main_box.add(toga.Label("Nudge timing strategy:"))
    app.nudge_type = toga.Selection(
        items=["Random", "Evenly spread"],
        value=settings.get("nudge_type", "Random"),
        style=Pack(padding_bottom=20)
    )
    main_box.add(app.nudge_type)

    # --- 👤 User Info ---
    main_box.add(toga.Label("👤 User Details", style=Pack(font_size=18, font_weight="bold", padding_top=20, padding_bottom=5)))

    user_email = getattr(app, "user_email", "Not logged in")
    main_box.add(toga.Label(f"Email: {user_email}", style=Pack(padding_bottom=10)))

    change_password_btn = toga.Button("Change Password", on_press=lambda w: print("🔧 TODO: Change password logic"), style=Pack(padding_bottom=5))
    logout_btn = toga.Button(
        "Log Off",
        on_press=lambda w: (
            setattr(app, "user_token", None),
            app.show_login_screen()
        ),
        style=Pack(padding_bottom=5)
    )
    save_btn = toga.Button("Save Settings", on_press=lambda w: handle_save(app), style=Pack(padding_top=10))

    main_box.add(change_password_btn)
    main_box.add(logout_btn)
    main_box.add(save_btn)

    return toga.ScrollContainer(content=main_box)


def handle_save(app):
    settings = {
        "nudges_per_day": int(app.nudges_input.value),
        "hours_start": str(app.start_hour.value),
        "hours_end": str(app.end_hour.value),
        "nudge_type": str(app.nudge_type.value),
    }

    print("📝 Attempting to save settings:", settings)
    try:
        save_settings_to_firestore(app.user_token, app.user_id, settings)
        app.nudge_settings = settings  # Update in-memory state
        print("✅ Settings saved to Firebase!")

        # ✅ Invalidate today's nudge schedule (force reschedule next time)
        set_meta_value(app.conn, "last_nudge_schedule_date", "")
        print("🧼 Cleared today's nudge schedule cache")

    except Exception as e:
        print("❌ Failed to save settings to Firebase", e)
        app.main_window.dialog(
            toga.ErrorDialog("Save Failed", "Could not save settings to the cloud.")
        )
