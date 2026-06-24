"""Claude/Anthropic-branded ttkbootstrap themes (light + dark) and helpers.

Palette from Anthropic brand guidelines:
  clay #d97757 (primary accent), cream #faf9f5, ink #141413,
  mid-gray #b0aea5, light-gray #e8e6dc, blue #6a9bcc, green #788c5d.
"""

from ttkbootstrap.style import ThemeDefinition

LIGHT = "claude-light"
DARK = "claude-dark"

_LIGHT_COLORS = {
    "primary": "#d97757",  # clay (operators / actions)
    "secondary": "#b0aea5",  # mid gray
    "success": "#788c5d",  # green (equals)
    "info": "#6a9bcc",  # blue (functions)
    "warning": "#d9a441",
    "danger": "#b3412a",
    "light": "#e8e6dc",
    "dark": "#141413",
    "bg": "#faf9f5",  # cream
    "fg": "#141413",  # ink
    "selectbg": "#d97757",
    "selectfg": "#faf9f5",
    "border": "#d9d6ca",
    "inputfg": "#141413",
    "inputbg": "#ffffff",
    "active": "#ece9df",
}

_DARK_COLORS = {
    "primary": "#d97757",
    "secondary": "#8c8a80",
    "success": "#9bb07a",
    "info": "#6a9bcc",
    "warning": "#d9a441",
    "danger": "#cc6b53",
    "light": "#3a3935",
    "dark": "#0f0f0e",
    "bg": "#1f1e1c",
    "fg": "#faf9f5",
    "selectbg": "#d97757",
    "selectfg": "#141413",
    "border": "#3a3935",
    "inputfg": "#faf9f5",
    "inputbg": "#2b2a27",
    "active": "#2b2a27",
}


def register_themes(style) -> None:
    """Register the Claude light/dark themes on a ttkbootstrap Style."""
    existing = style.theme_names()
    if LIGHT not in existing:
        style.register_theme(ThemeDefinition(LIGHT, _LIGHT_COLORS, "light"))
    if DARK not in existing:
        style.register_theme(ThemeDefinition(DARK, _DARK_COLORS, "dark"))


def configure_fonts(root) -> None:
    """Bump default font sizes for a calmer, more readable layout."""
    import tkinter.font as tkfont

    for name, size in (("TkDefaultFont", 12), ("TkTextFont", 12), ("TkMenuFont", 12)):
        try:
            tkfont.nametofont(name).configure(family="Helvetica", size=size)
        except Exception:
            pass
