from PIL import Image, ImageDraw
import math
import colorsys

def generate_pie_chart_image(grouped_data, width=300, height=300):
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    total = sum(grouped_data.values())
    if total == 0:
        return image

    center = (width // 2, height // 2)
    radius = min(width, height) // 2 - 10
    angle_start = 0

    for i, (label, value) in enumerate(grouped_data.items()):
        angle_extent = (value / total) * 360
        hue = i / len(grouped_data)
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.6, 0.8)]
        fill_color = (r, g, b)

        # Draw pie slice
        draw.pieslice(
            [center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius],
            angle_start,
            angle_start + angle_extent,
            fill=fill_color
        )

        # Mid-angle for label
        mid_angle_rad = math.radians(angle_start + angle_extent / 2)
        label_x = center[0] + radius * 0.5 * math.cos(mid_angle_rad)
        label_y = center[1] + radius * 0.5 * math.sin(mid_angle_rad)
        draw.text((label_x, label_y), label[:10], fill="black")

        angle_start += angle_extent

    return image
