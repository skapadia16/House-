
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class ColorPalette:
    sky_top: Tuple[int, int, int]
    sky_bottom: Tuple[int, int, int]
    ground_top: Tuple[int, int, int]
    ground_bottom: Tuple[int, int, int]
    house_body: Tuple[int, int, int]
    house_roof: Tuple[int, int, int]
    house_door: Tuple[int, int, int]
    house_trim: Tuple[int, int, int]
    tree_trunk: Tuple[int, int, int]
    tree_foliage_light: Tuple[int, int, int]
    tree_foliage_dark: Tuple[int, int, int]
    cloud_white: Tuple[int, int, int, int] # RGBA
    sun_moon: Tuple[int, int, int]
    shadow: Tuple[int, int, int, int] # RGBA

# Premium "Children's Book" Palette (Day)
DAY_THEME = ColorPalette(
    sky_top=(135, 206, 250),      # Soft Sky Blue
    sky_bottom=(224, 255, 255),   # Light Cyan
    ground_top=(144, 238, 144),   # Light Green
    ground_bottom=(34, 139, 34),  # Forest Green
    house_body=(255, 250, 240),   # Floral White
    house_roof=(205, 92, 92),     # Indian Red
    house_door=(139, 69, 19),     # Saddle Brown
    house_trim=(112, 128, 144),   # Slate Gray
    tree_trunk=(101, 67, 33),     # Dark Brown
    tree_foliage_light=(154, 205, 50), # Yellow Green
    tree_foliage_dark=(107, 142, 35),  # Olive Drab
    cloud_white=(255, 255, 255, 200),
    sun_moon=(255, 215, 0),       # Gold
    shadow=(50, 50, 60, 100)      # Soft cool shadow
)

@dataclass
class Config:
    width: int = 1200
    height: int = 800
    fps: int = 60
    title: str = "Cozy House Scene"
    palette: ColorPalette = field(default_factory=lambda: DAY_THEME)
    
    # Proportions based on screen height
    horizon_ratio: float = 0.65

    house_scale: float = 0.4
