"""
ui/styles.py
------------
Folha de estilos CSS para a interface PyGTK.
Carregue com ui.styles.apply_css(widget).
"""

from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

CSS = """
/* ===== Paleta ===== */
@define-color bg_dark       #0f1117;
@define-color bg_surface    #1a1d2e;
@define-color bg_card       #22263a;
@define-color accent        #6c63ff;
@define-color accent_light  #9b95ff;
@define-color text_primary  #e8eaf6;
@define-color text_secondary #9ea7c4;
@define-color success       #4caf50;
@define-color warning       #ff9800;
@define-color error_color   #f44336;
@define-color border_color  #2e3250;

/* ===== Janela principal ===== */
window, .main-window {
    background-color: @bg_dark;
    color: @text_primary;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* ===== Barra de título / header bar ===== */
headerbar {
    background-color: @bg_surface;
    border-bottom: 1px solid @border_color;
    color: @text_primary;
    min-height: 48px;
}

headerbar .title {
    font-weight: 700;
    font-size: 15px;
    color: @text_primary;
}

/* ===== Sidebar ===== */
.sidebar {
    background-color: @bg_surface;
    border-right: 1px solid @border_color;
    padding: 8px;
}

/* ===== Cards de resultado ===== */
.result-card {
    background-color: @bg_card;
    border-radius: 10px;
    border: 1px solid @border_color;
    padding: 14px 16px;
    margin: 6px 4px;
}

.result-card:hover {
    border-color: @accent;
}

.result-score {
    font-size: 11px;
    color: @accent_light;
    font-weight: 600;
}

.result-docname {
    font-size: 12px;
    color: @text_secondary;
    font-style: italic;
}

.result-text {
    color: @text_primary;
    font-size: 13px;
}

/* ===== Campo de busca ===== */
.search-entry {
    background-color: @bg_card;
    color: @text_primary;
    border: 1.5px solid @border_color;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
}

.search-entry:focus {
    border-color: @accent;
}

/* ===== Botões ===== */
.btn-primary {
    background-color: @accent;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
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
    background-color: transparent;
    color: @accent_light;
    border: 1.5px solid @accent;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
}

.btn-secondary:hover {
    background-color: alpha(@accent, 0.12);
}

/* ===== Barra de progresso ===== */
progressbar trough {
    background-color: @bg_card;
    border-radius: 4px;
    min-height: 6px;
}

progressbar progress {
    background-color: @accent;
    border-radius: 4px;
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
    background-color: alpha(@accent, 0.10);
}

.doc-row:selected {
    background-color: alpha(@accent, 0.22);
    color: @accent_light;
}

/* ===== Labels de status ===== */
.status-label {
    color: @text_secondary;
    font-size: 12px;
    padding: 4px 8px;
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

    screen = Gdk.Screen.get_default()
    Gtk.StyleContext.add_provider_for_screen(
        screen,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
