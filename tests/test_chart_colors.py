import ast
import re
import pytest

def get_app_source():
    with open("app.py", "r") as f:
        return f.read()

BANNED_COLORS = [
    "#005EA5", "#00A3E0", "#6ECEB2",  # NSW Health colors
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",  # Plotly defaults
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    "#C00000", "#00843D", "#F7931E", "#6B21A8", "#0891B2",  # Legacy colors
]

def test_no_hardcoded_plotly_default_colors():
    source = get_app_source()
    for color in BANNED_COLORS:
        assert color.lower() not in source.lower(), (
            f"Found banned hardcoded color {color} in app.py — use PALETTE instead"
        )

def test_imports_color_theme():
    source = get_app_source()
    assert "from color_theme import" in source

def test_no_bare_hex_in_marker_color():
    source = get_app_source()
    pattern = r'marker_color\s*=\s*["\']#[0-9a-fA-F]{6}["\']'
    matches = re.findall(pattern, source)
    assert len(matches) == 0, (
        f"Found hardcoded hex in marker_color: {matches} — use PALETTE['...'] instead"
    )

def test_no_bare_hex_in_line_color():
    source = get_app_source()
    pattern = r'line_color\s*=\s*["\']#[0-9a-fA-F]{6}["\']'
    matches = re.findall(pattern, source)
    assert len(matches) == 0, (
        f"Found hardcoded hex in line_color: {matches} — use PALETTE['...'] instead"
    )

def test_no_bare_hex_in_color_discrete_sequence():
    source = get_app_source()
    pattern = r'color_discrete_sequence\s*=\s*\[.*?#[0-9a-fA-F]{6}.*?\]'
    matches = re.findall(pattern, source, re.DOTALL)
    assert len(matches) == 0, (
        f"Found hardcoded hex in color_discrete_sequence — use CHART_SEQUENCE instead"
    )