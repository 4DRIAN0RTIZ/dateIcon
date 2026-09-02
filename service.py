from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Optional

from config import THEMES, MONTHS, SIZES_ALLOWED, DEFAULT_FONT_PATH


def parse_hex_color(hex_str: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    digits = hex_str[1:] if hex_str.startswith('#') else hex_str
    if len(digits) != 6 or any(c not in "0123456789abcdefABCDEF" for c in digits):
        raise ValueError(
            f"Invalid hex color: {hex_str!r}. "
            "Expected 6 hex digits, optionally prefixed with '#'."
        )
    return tuple(int(digits[i:i+2], 16) for i in (0, 2, 4))


def parse_date(date_str: str) -> tuple:
    """Parse date string in DD_MM format."""
    try:
        dd_str, mm_str = date_str.split('_')
        dd = int(dd_str)
        mm = int(mm_str)
        if not (1 <= mm <= 12):
            raise ValueError("Month must be between 1 and 12")
        if not (1 <= dd <= 31):
            raise ValueError("Day must be between 1 and 31")
        return dd, mm
    except (ValueError, AttributeError):
        raise ValueError("Invalid date format. Use DD_MM format")


class DateIconService:
    def __init__(self, font_path: str = DEFAULT_FONT_PATH):
        self.font_path = font_path

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load font with fallback to default."""
        try:
            return ImageFont.truetype(self.font_path, size)
        except IOError:
            return ImageFont.load_default()

    def _get_colors(
        self,
        theme: str,
        custom_bar: Optional[str],
        custom_bg: Optional[str],
        custom_text: Optional[str],
    ) -> tuple:
        """Get color configuration based on theme."""
        if theme == "custom":
            bar = custom_bar or "e38528"
            bg = custom_bg or "fff8f0"
            text = custom_text or "1a1a1a"
        else:
            theme_data = THEMES.get(theme, THEMES["default"])
            bar = theme_data["bar_color"]
            bg = theme_data["bg_color"]
            text = theme_data["text_color"]

        return parse_hex_color(bar), parse_hex_color(bg), parse_hex_color(text)

    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        coords: list,
        radius: int,
        outline=None,
        width: int = 1,
    ):
        """Draw a rounded rectangle."""
        x1, y1 = coords[0]
        x2, y2 = coords[1]

        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=width)
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=width)

        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)

    def generate(
        self,
        date_str: str,
        size: int = 64,
        theme: str = "default",
        lang: str = "es",
        custom_bar_color: Optional[str] = None,
        custom_bg_color: Optional[str] = None,
        custom_text_color: Optional[str] = None,
    ) -> BytesIO:
        """Generate a date icon image."""
        dd, mm = parse_date(date_str)

        if size not in SIZES_ALLOWED:
            raise ValueError(f"Invalid size. Allowed sizes: {SIZES_ALLOWED}")

        canvas_size = size
        final_size = canvas_size

        scale_factor = 8 if canvas_size <= 32 else (4 if canvas_size < 64 else 1)
        canvas_size *= scale_factor

        bar_rgb, bg_rgb, text_rgb = self._get_colors(
            theme, custom_bar_color, custom_bg_color, custom_text_color
        )

        month_names = MONTHS.get(lang, MONTHS["es"])

        img = Image.new('RGB', (canvas_size, canvas_size), bg_rgb)
        draw = ImageDraw.Draw(img)

        radius = int(canvas_size * 0.1)
        draw.rectangle([(1, 1), (canvas_size - 2, canvas_size - 2)], width=2)
        self._draw_rounded_rectangle(
            draw, [(1, 1), (canvas_size - 2, canvas_size - 2)], radius, width=2
        )

        bar_height = int(canvas_size * 0.45)
        draw.rectangle([(1, 1), (canvas_size - 2, bar_height)], fill=bar_rgb)

        month_font = self._load_font(int(bar_height * 0.9))
        day_font = self._load_font(int(canvas_size * 0.5))

        month_text = month_names[mm - 1].upper()
        month_bbox = draw.textbbox((0, 0), month_text, font=month_font)
        month_x = (canvas_size - (month_bbox[2] - month_bbox[0])) / 2
        month_y = (bar_height - (month_bbox[3] - month_bbox[1])) / 2 * -0.6
        draw.text((month_x, month_y), month_text, fill='white', font=month_font)

        day_text = str(dd)
        day_bbox = draw.textbbox((0, 0), day_text, font=day_font)
        day_x = (canvas_size - (day_bbox[2] - day_bbox[0])) / 2
        day_y = bar_height + (canvas_size - bar_height - (day_bbox[3] - day_bbox[1])) / 2 * -0.2
        draw.text((day_x, day_y), day_text, fill=text_rgb, font=day_font)

        if scale_factor > 1:
            img = img.resize((final_size, final_size), Image.Resampling.LANCZOS)

        img_io = BytesIO()
        img.save(img_io, 'PNG', optimize=True)
        img_io.seek(0)

        return img_io
