from PIL import Image, ImageDraw
import os

# ✅ Define fixed order and colors
GOAL_ORDER = ["Physical", "Biological", "Beyond Biology"]
TIME_ORDER = ["Immediate Term", "Short Term", "Medium Term", "Long Term"]
FIXED_COLORS = {
    "Physical": (255, 99, 132),
    "Biological": (54, 162, 235),
    "Beyond Biology": (255, 206, 86),
    "Immediate Term": (75, 192, 192),
    "Short Term": (153, 102, 255),
    "Medium Term": (255, 159, 64),
    "Long Term": (100, 100, 100)
}

def generate_bar_chart_image(grouped_data, width=400, height=300, category_type="goal"):
    keys = GOAL_ORDER if category_type == "goal" else TIME_ORDER
    values = [grouped_data.get(k, 0) for k in keys]

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    if not values or max(values) == 0:
        return image

    max_value = max(values)
    bar_width = width // len(keys)
    scale = (height - 40) / max_value if max_value else 1

    for i, (label, value) in enumerate(zip(keys, values)):
        x0 = i * bar_width + 10
        x1 = x0 + bar_width - 20
        y1 = height - 20
        y0 = y1 - int(value * scale)
        bar_color = FIXED_COLORS.get(label, (200, 200, 200))  # fallback to gray

        draw.rectangle([x0, y0, x1, y1], fill=bar_color)
        draw.text((x0, height - 15), label[:10], fill="black")

    return image
