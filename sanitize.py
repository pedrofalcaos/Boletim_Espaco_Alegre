"""
Sanitização de HTML de texto rico (descrição final do relatório).

A descrição é escrita pelas professoras num editor de texto rico e exibida
como HTML para os responsáveis. Para evitar XSS armazenado, limpamos o HTML
mantendo apenas uma lista branca de tags/atributos seguros — removendo
scripts, manipuladores de evento (onclick…), iframes, etc.

Cor do texto é preservada via <font color="..."> (atributo seguro). O atributo
`style` é descartado de propósito, pois o CSS inline não é sanitizado a fundo e
poderia carregar vetores (ex.: url(javascript:...)).
"""
import nh3

_TAGS = {
    "a", "b", "blockquote", "br", "div", "em", "font", "h3", "h4",
    "i", "li", "ol", "p", "span", "strong", "u", "s", "ul", "img",
}

_ATTRS = {
    "a":    {"href", "title"},
    "font": {"color", "face"},
    "img":  {"src", "alt", "width", "height"},
    "div":  {"align"},
    "p":    {"align"},
}

# Só links/imagens com esses esquemas; javascript:/data:text/html são removidos.
_URL_SCHEMES = {"http", "https", "mailto"}


def sanitizar_html(html: str) -> str:
    """Retorna o HTML limpo e seguro para exibição ao responsável."""
    if not html:
        return ""
    return nh3.clean(
        html,
        tags=_TAGS,
        attributes=_ATTRS,
        url_schemes=_URL_SCHEMES,
        link_rel="noopener noreferrer",
    )
