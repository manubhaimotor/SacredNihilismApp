import random
from datetime import datetime, timedelta

def generate_nudge_times(nudges_per_day, start_hour, end_hour, strategy="evenly"):
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = today + timedelta(hours=start_hour)
    end = today + timedelta(hours=end_hour)

    if nudges_per_day <= 0 or start >= end:
        print("⚠️ Invalid nudge scheduling parameters.")
        return []

    time_range_seconds = int((end - start).total_seconds())

    if strategy == "random":
        offsets = sorted(random.sample(range(time_range_seconds), nudges_per_day))
    else:  # evenly
        interval = time_range_seconds / nudges_per_day
        offsets = [int(interval * i + interval / 2) for i in range(nudges_per_day)]

    scheduled_times = [start + timedelta(seconds=offset) for offset in offsets]

    print("📅 Today's nudges scheduled at:")
    for time in scheduled_times:
        print(" -", time.strftime("%H:%M:%S"))

    return scheduled_times
