import re
import pytest
from color_theme import PALETTE, CHART_SEQUENCE, HEATMAP_SCALE, PLOTLY_LAYOUT_DEFAULTS

HEX_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")

def test_all_palette_values_are_valid_hex():
    for name, color in PALETTE.items():
        assert HEX_PATTERN.match(color), f"{name}: {color} is not valid hex"

def test_chart_sequence_has_5_colors():
    assert len(CHART_SEQUENCE) == 5

def test_chart_sequence_all_from_palette():
    palette_values = set(PALETTE.values())
    for color in CHART_SEQUENCE:
        assert color in palette_values, f"{color} not in PALETTE"

def test_no_duplicate_colors_in_palette():
    values = list(PALETTE.values())
    assert len(values) == len(set(values))

def test_heatmap_scale_starts_at_0_ends_at_1():
    assert HEATMAP_SCALE[0][0] == 0.0
    assert HEATMAP_SCALE[-1][0] == 1.0

def test_heatmap_scale_uses_palette_colors():
    palette_values = set(PALETTE.values())
    for _, color in HEATMAP_SCALE:
        assert color in palette_values

def test_alert_is_dark_red():
    r = int(PALETTE["alert"][1:3], 16)
    g = int(PALETTE["alert"][3:5], 16)
    b = int(PALETTE["alert"][5:7], 16)
    assert r > g and r > b, "Alert should be red-dominant"

def test_plotly_layout_defaults_has_required_keys():
    required = ["paper_bgcolor", "plot_bgcolor", "font", "xaxis", "yaxis"]
    for key in required:
        assert key in PLOTLY_LAYOUT_DEFAULTS

def test_plotly_gridcolor_is_neutral():
    assert PLOTLY_LAYOUT_DEFAULTS["xaxis"]["gridcolor"] == PALETTE["neutral"]
    assert PLOTLY_LAYOUT_DEFAULTS["yaxis"]["gridcolor"] == PALETTE["neutral"]