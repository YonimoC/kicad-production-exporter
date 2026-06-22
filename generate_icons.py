"""
Generate placeholder icons for the plugin.
Run this script with Pillow installed: pip install Pillow && python generate_icons.py
"""

import os

def generate_icons():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("请先安装 Pillow: pip install Pillow")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugins_dir = os.path.join(script_dir, "plugins")
    resources_dir = os.path.join(script_dir, "resources")

    os.makedirs(os.path.join(plugins_dir, "icons"), exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)

    def create_icon(size, filepath, text="P"):
        """Create a simple icon with text."""
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw a rounded rectangle background
        margin = 2
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=size // 6,
            fill=(49, 130, 189)  # Steel blue
        )

        # Draw text
        try:
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (size - text_w) // 2
        text_y = (size - text_h) // 2 - 1
        draw.text((text_x, text_y), text, fill="white", font=font)

        img.save(filepath, "PNG")
        print(f"  ✓ {filepath} ({size}x{size})")

    # Toolbar icons (24x24) - for the button in PCB editor
    light_icon = os.path.join(plugins_dir, "icons", "icon-light.png")
    dark_icon = os.path.join(plugins_dir, "icons", "icon-dark.png")
    create_icon(24, light_icon, "P")   # Light theme
    create_icon(24, dark_icon, "P")     # Dark theme

    # PCM icon (64x64) - for the Plugin and Content Manager
    pcm_icon = os.path.join(resources_dir, "icon.png")
    create_icon(64, pcm_icon, "P")

    print("\n图标生成完成！")
    print(f"  工具栏图标: {plugins_dir}/icons/")
    print(f"  PCM 图标:   {resources_dir}/icon.png")


if __name__ == "__main__":
    generate_icons()
