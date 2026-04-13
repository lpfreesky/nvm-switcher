from PIL import Image, ImageDraw, ImageFont
import os


def create_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    r = radius
    draw.ellipse([x0, y0, x0 + r * 2, y0 + r * 2], fill=fill)
    draw.ellipse([x1 - r * 2, y0, x1, y0 + r * 2], fill=fill)
    draw.ellipse([x0, y1 - r * 2, x0 + r * 2, y1], fill=fill)
    draw.ellipse([x1 - r * 2, y1 - r * 2, x1, y1], fill=fill)
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)


def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = size // 16
    radius = size // 5

    # 绿色渐变模拟：底层深绿，上层浅绿叠加
    create_rounded_rect(draw, [margin, margin, size - margin, size - margin], radius, fill="#2E7D32")
    highlight = size // 8
    create_rounded_rect(
        draw,
        [margin, margin, size - margin, size - margin - highlight],
        radius,
        fill="#4CAF50",
    )

    # 文字 "JS"
    text = "JS"
    font_size = int(size * 0.55)
    try:
        font = ImageFont.truetype("segoeui.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2
    y = (size - text_h) // 2 - size // 20
    draw.text((x, y), text, font=font, fill="white")
    return img


def main():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    for s in sizes:
        images.append(make_icon(s))
    output_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    images[0].save(output_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Icon saved to {output_path}")


if __name__ == "__main__":
    main()
