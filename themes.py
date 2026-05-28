"""VS Code 风格主题系统"""

import json, os

THEMES = {
    "github-dark": {
        "name": "GitHub Dark",
        "bg": "#0d1117", "bg2": "#161b22", "bg3": "#21262d",
        "border": "#30363d", "fg": "#e6edf3", "fg2": "#8b949e",
        "accent": "#f78166", "accent2": "#ffa198", "green": "#3fb950",
        "green2": "#56d364", "blue": "#58a6ff", "purple": "#bc8cff",
        "yellow": "#d29922", "red": "#f85149", "pink": "#db61a2", "cyan": "#39d2c0",
    },
    "one-dark": {
        "name": "One Dark Pro",
        "bg": "#282c34", "bg2": "#21252b", "bg3": "#2c313a",
        "border": "#181a1f", "fg": "#abb2bf", "fg2": "#5c6370",
        "accent": "#e06c75", "accent2": "#be5046", "green": "#98c379",
        "green2": "#7ec76e", "blue": "#61afef", "purple": "#c678dd",
        "yellow": "#e5c07b", "red": "#e06c75", "pink": "#c678dd", "cyan": "#56b6c2",
    },
    "dracula": {
        "name": "Dracula",
        "bg": "#282a36", "bg2": "#21222c", "bg3": "#343746",
        "border": "#191a21", "fg": "#f8f8f2", "fg2": "#6272a4",
        "accent": "#ff79c6", "accent2": "#ff92d0", "green": "#50fa7b",
        "green2": "#69ff94", "blue": "#8be9fd", "purple": "#bd93f9",
        "yellow": "#f1fa8c", "red": "#ff5555", "pink": "#ff79c6", "cyan": "#8be9fd",
    },
    "nord": {
        "name": "Nord",
        "bg": "#2e3440", "bg2": "#3b4252", "bg3": "#434c5e",
        "border": "#4c566a", "fg": "#eceff4", "fg2": "#7b88a1",
        "accent": "#bf616a", "accent2": "#d08770", "green": "#a3be8c",
        "green2": "#b9d09c", "blue": "#81a1c1", "purple": "#b48ead",
        "yellow": "#ebcb8b", "red": "#bf616a", "pink": "#b48ead", "cyan": "#88c0d0",
    },
    "monokai": {
        "name": "Monokai",
        "bg": "#272822", "bg2": "#1e1f1c", "bg3": "#3e3d32",
        "border": "#49483e", "fg": "#f8f8f2", "fg2": "#75715e",
        "accent": "#f92672", "accent2": "#fd5ff0", "green": "#a6e22e",
        "green2": "#b7f03d", "blue": "#66d9ef", "purple": "#ae81ff",
        "yellow": "#e6db74", "red": "#f92672", "pink": "#f92672", "cyan": "#a1efe4",
    },
    "tokyo-night": {
        "name": "Tokyo Night",
        "bg": "#1a1b26", "bg2": "#16161e", "bg3": "#292e42",
        "border": "#3b4261", "fg": "#c0caf5", "fg2": "#565f89",
        "accent": "#f7768e", "accent2": "#ff9e64", "green": "#9ece6a",
        "green2": "#b9f27c", "blue": "#7aa2f7", "purple": "#9d7cd8",
        "yellow": "#e0af68", "red": "#f7768e", "pink": "#bb9af7", "cyan": "#7dcfff",
    },
    "solarized-dark": {
        "name": "Solarized Dark",
        "bg": "#002b36", "bg2": "#073642", "bg3": "#094552",
        "border": "#586e75", "fg": "#eee8d5", "fg2": "#839496",
        "accent": "#cb4b16", "accent2": "#dc322f", "green": "#859900",
        "green2": "#a3b900", "blue": "#268bd2", "purple": "#6c71c4",
        "yellow": "#b58900", "red": "#dc322f", "pink": "#d33682", "cyan": "#2aa198",
    },
    "github-light": {
        "name": "GitHub Light",
        "bg": "#ffffff", "bg2": "#f6f8fa", "bg3": "#eaeef2",
        "border": "#d0d7de", "fg": "#1f2328", "fg2": "#656d76",
        "accent": "#cf222e", "accent2": "#a40e26", "green": "#1a7f37",
        "green2": "#26a148", "blue": "#0969da", "purple": "#8250df",
        "yellow": "#9a6700", "red": "#cf222e", "pink": "#bf3989", "cyan": "#1b7c83",
    },
    "one-light": {
        "name": "One Light",
        "bg": "#fafafa", "bg2": "#f0f0f0", "bg3": "#e5e5e6",
        "border": "#d4d4d6", "fg": "#383a42", "fg2": "#a0a1a7",
        "accent": "#e45649", "accent2": "#ca1243", "green": "#50a14f",
        "green2": "#3d8f3d", "blue": "#4078f2", "purple": "#a626a4",
        "yellow": "#c18401", "red": "#e45649", "pink": "#a626a4", "cyan": "#0184bc",
    },
}

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".theme_config")


def load_theme() -> str:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("theme", "github-dark")
    except Exception:
        return "github-dark"


def save_theme(name: str):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"theme": name}, f)
    except Exception:
        pass


def get_theme(name: str) -> dict:
    return THEMES.get(name, THEMES["github-dark"])


def list_themes() -> list:
    return [(k, v["name"]) for k, v in THEMES.items()]
