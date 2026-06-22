"""Ícones SVG inline (estilo outline, traço fino) usados no lugar de emojis
nos botões de ação do site, seguindo a estética Liquid Glass."""


def _svg(paths: str, size: int = 14) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'style="display:inline-block;vertical-align:-2px;margin-right:4px;">{paths}</svg>')


ICON_EDIT = _svg('<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z"/>')
ICON_VIEW = _svg('<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z"/><circle cx="12" cy="12" r="3"/>')
ICON_CLIPBOARD = _svg('<rect width="7" height="3" x="8.5" y="2" rx="1"/>'
                       '<path d="M14 4h2a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
                       '<path d="M9 12h6"/><path d="M9 16h6"/>')
_PRINTER_PATHS = ('<polyline points="5 8 5 2 15 2 15 8"/>'
                   '<path d="M5 15H3a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-2"/>'
                   '<rect width="10" height="6" x="5" y="12"/>')
ICON_PRINTER = _svg(_PRINTER_PATHS)


def icon_printer(size: int = 14) -> str:
    return _svg(_PRINTER_PATHS, size)
ICON_LOCK = _svg('<rect width="14" height="9" x="5" y="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>')
ICON_UNLOCK = _svg('<rect width="14" height="9" x="5" y="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 7.6-1.8"/>')
ICON_REFRESH = _svg('<path d="M3 12a9 9 0 0 1 15.5-6.3M21 12a9 9 0 0 1-15.5 6.3"/>'
                     '<path d="M21 3v6h-6"/><path d="M3 21v-6h6"/>')
ICON_TOOL = _svg('<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76Z"/>')
ICON_KEY = _svg('<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/>')
ICON_PLUS = _svg('<path d="M12 5v14"/><path d="M5 12h14"/>')
ICON_TRASH = _svg('<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>'
                   '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>')


def dot(color: str, size: int = 8) -> str:
    return (f'<span style="display:inline-block;width:{size}px;height:{size}px;'
            f'border-radius:50%;background:{color};margin-right:5px;vertical-align:middle;"></span>')
