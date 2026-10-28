"""
ui/styles.py
------------
Folha de estilos CSS para a interface PyGTK.
Carregue com ui.styles.apply_css(widget).
"""

from __future__ import annotations

import gi
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk

CSS = """
/* ===== Tema inspirado no macOS (Dark) ===== */
@define-color bg_dark        #1c1c1e;
@define-color bg_surface     #252527;
@define-color bg_elevated    #2c2c2e;
@define-color bg_card        #303033;
@define-color accent         #0a84ff;
@define-color accent_light   #409cff;
@define-color text_primary   #f5f5f7;
@define-color text_secondary #a1a1a6;
@define-color success        #30d158;
@define-color error_color    #ff453a;
@define-color border_color   #3a3a3c;

/* ===== Janela principal ===== */
window, .main-window {
    background-color: @bg_dark;
    color: @text_primary;
    font-family: "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Cantarell", sans-serif;
    font-size: 13px;
}

/* ===== Barra de título / header bar ===== */
headerbar {
    background-color: #242426;
    border-bottom: 1px solid @border_color;
    color: @text_primary;
    min-height: 44px;
}

headerbar .title {
    font-weight: 600;
    font-size: 13px;
    color: @text_primary;
}

/* ===== Sidebar ===== */
.sidebar {
    background-color: @bg_surface;
    border-right: 1px solid @border_color;
    padding: 6px;
}

.sidebar-title {
    color: @text_primary;
    font-size: 15px;
    font-weight: 700;
}

/* ===== Cards de resultado ===== */
.result-card {
    background-color: @bg_card;
    border-radius: 12px;
    border: 1px solid @border_color;
    padding: 15px 16px;
    margin: 7px 4px;
}

.result-card:hover {
    border-color: alpha(@accent, 0.7);
    background-color: #353539;
}

.result-score {
    font-size: 11px;
    color: @accent_light;
    font-weight: 600;
}

.result-docname {
    font-size: 12px;
    color: @text_secondary;
    font-style: normal;
}

.result-text {
    color: @text_primary;
    font-size: 13px;
}

/* ===== Campo de busca ===== */
.search-entry {
    background-color: #343437;
    color: @text_primary;
    border: 1px solid #464649;
    border-radius: 10px;
    padding: 9px 12px;
    font-size: 14px;
}

.search-entry:focus {
    border-color: alpha(@accent, 0.9);
    box-shadow: 0 0 0 2px alpha(@accent, 0.30);
}

/* ===== Botões ===== */
.btn-primary {
    background-color: @accent;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

.btn-primary:hover {
    background-color: @accent_light;
}

.btn-primary:disabled {
    background-color: @border_color;
    color: @text_secondary;
}

.btn-secondary {
    background-color: #3a3a3c;
    color: @text_primary;
    border: 1px solid #48484a;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
}

.btn-secondary:hover {
    background-color: #48484a;
}

.btn-toolbar {
    background-color: transparent;
    color: @text_secondary;
    border: none;
    border-radius: 8px;
    padding: 6px 9px;
    font-size: 16px;
}

.btn-toolbar:hover {
    background-color: #3a3a3c;
    color: @text_primary;
}

/* ===== Barra de progresso ===== */
progressbar trough {
    background-color: #343437;
    border: 1px solid @border_color;
    border-radius: 8px;
    min-height: 18px;
}

progressbar progress {
    background-image: linear-gradient(90deg, #0a84ff, #5e5ce6);
    border-radius: 7px;
}

progressbar text {
    color: @text_primary;
    font-size: 11px;
    font-weight: 700;
}

/* ===== Lista de documentos (sidebar) ===== */
.doc-row {
    background-color: transparent;
    border-radius: 6px;
    padding: 8px 10px;
    color: @text_primary;
    font-size: 13px;
}

.doc-row:hover {
    background-color: #353538;
}

.doc-row:selected {
    background-color: #0a5fbd;
    color: white;
}

/* ===== Labels de status ===== */
.status-label {
    color: @text_secondary;
    font-size: 12px;
    padding: 6px 8px;
}

.status-success {
    color: @success;
}

.status-error {
    color: @error_color;
}

/* ===== ScrolledWindow ===== */
scrolledwindow {
    background-color: @bg_dark;
}

scrollbar slider {
    background-color: #636366;
    border-radius: 8px;
    min-width: 6px;
    min-height: 6px;
}

scrollbar slider:hover {
    background-color: #8e8e93;
}

/* ===== Separadores ===== */
separator {
    background-color: @border_color;
    min-height: 1px;
}
"""


def apply_css() -> None:
    """Aplica a folha de estilos globalmente (GTK 3)."""
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.encode("utf-8"))

    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
