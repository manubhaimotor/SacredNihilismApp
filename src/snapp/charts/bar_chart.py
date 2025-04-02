from PIL import Image, ImageDraw, ImageFont
import os
import colorsys

def generate_bar_chart_image(grouped_data, width=400, height=300):
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    keys = list(grouped_data.keys())
    values = list(grouped_data.values())

    if not values:
        return image

    max_value = max(values)
    bar_width = width // len(values)
    scale = (height - 40) / max_value if max_value else 1

    for i, (label, value) in enumerate(grouped_data.items()):
        x0 = i * bar_width + 10
        x1 = x0 + bar_width - 20
        y1 = height - 20
        y0 = y1 - int(value * scale)

        # Assign a different color to each bar using HSV
        hue = i / len(grouped_data)
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.6, 0.8)]
        bar_color = (r, g, b)

        draw.rectangle([x0, y0, x1, y1], fill=bar_color)
        draw.text((x0, height - 15), label[:10], fill="black")


    return image
