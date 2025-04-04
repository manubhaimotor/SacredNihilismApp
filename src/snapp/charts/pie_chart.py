from PIL import Image, ImageDraw
import math

# ✅ Reuse the same fixed order and colors
GOAL_ORDER = ["Physical", "Biological", "Biology+"]
TIME_ORDER = ["Immediate Term", "Short Term", "Medium Term", "Long Term"]
FIXED_COLORS = {
    "Physical": (255, 99, 132),
    "Biological": (54, 162, 235),
    "Biology+": (255, 206, 86),
    "Immediate Term": (75, 192, 192),
    "Short Term": (153, 102, 255),
    "Medium Term": (255, 159, 64),
    "Long Term": (100, 100, 100)
}

def generate_pie_chart_image(grouped_data, width=300, height=300, category_type="goal"):
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    keys = GOAL_ORDER if category_type == "goal" else TIME_ORDER
    values = [grouped_data.get(k, 0) for k in keys]
    total = sum(values)
    if total == 0:
        return image

    center = (width // 2, height // 2)
    radius = min(width, height) // 2 - 10
    angle_start = 0

    for label, value in zip(keys, values):
        if value == 0:
            continue  # skip drawing 0-value slices
        angle_extent = (value / total) * 360
        fill_color = FIXED_COLORS.get(label, (200, 200, 200))

        draw.pieslice(
            [center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius],
            angle_start,
            angle_start + angle_extent,
            fill=fill_color
        )

        # Add label at mid-angle
        mid_angle = math.radians(angle_start + angle_extent / 2)
        label_x = center[0] + radius * 0.5 * math.cos(mid_angle)
        label_y = center[1] + radius * 0.5 * math.sin(mid_angle)
        draw.text((label_x, label_y), label[:10], fill="black")

        angle_start += angle_extent

    return image
