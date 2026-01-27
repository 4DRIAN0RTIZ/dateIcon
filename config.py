import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class Language(str, Enum):
    ES = "es"
    EN = "en"
    FR = "fr"
    DE = "de"
    PT = "pt"


class Theme(str, Enum):
    DEFAULT = "default"
    DARK = "dark"
    OCEAN = "ocean"
    FOREST = "forest"
    SUNSET = "sunset"
    CUSTOM = "custom"


THEMES = {
    "default": {"bar_color": "e38528", "bg_color": "fff8f0", "text_color": "1a1a1a"},
    "dark": {"bar_color": "222222", "bg_color": "1a1a1a", "text_color": "ffffff"},
    "ocean": {"bar_color": "0077cc", "bg_color": "e6f3ff", "text_color": "003366"},
    "forest": {"bar_color": "2e7d32", "bg_color": "e8f5e9", "text_color": "1b5e20"},
    "sunset": {"bar_color": "d84315", "bg_color": "fbe9e7", "text_color": "bf360c"},
}

MONTHS = {
    "es": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "fr": ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"],
    "de": ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    "pt": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
}

LANGUAGES_INFO = {
    "es": "Spanish",
    "en": "English",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
}

SIZES_ALLOWED = [16, 24, 32, 48, 64, 128, 256, 512, 1024]

DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# Server configuration
class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "4"))

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "100"))

    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Production mode
    PRODUCTION: bool = os.getenv("PRODUCTION", "false").lower() == "true"


settings = Settings()
