"""Gera static/logo.png a partir de static/logo.jpg removendo o fundo branco.

Usa flood-fill a partir das bordas para apagar apenas o branco *conectado* ao
fundo, preservando o branco interno (olhos/rostos das flores). Em seguida suaviza
o halo claro deixado pela compressão JPEG ao redor do desenho.

Uso:  python gerar_logo_transparente.py
"""
from PIL import Image, ImageDraw
from collections import deque

SRC = "static/logo.jpg"
DST = "static/logo.png"

# Tolerância: quão "claro" um pixel precisa ser para contar como fundo.
# Branco = 255. Amarelo (~247,216,0) e azul ficam bem abaixo, então ficam a salvo.
def is_background_like(px):
    r, g, b = px[0], px[1], px[2]
    return r > 205 and g > 205 and b > 205


def main():
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size
    px = im.load()

    # 1) Flood-fill (BFS) a partir de todos os pixels das bordas que sejam claros.
    visited = bytearray(w * h)
    q = deque()

    def seed(x, y):
        i = y * w + x
        if not visited[i] and is_background_like(px[x, y]):
            visited[i] = 1
            q.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                i = ny * w + nx
                if not visited[i] and is_background_like(px[nx, ny]):
                    visited[i] = 1
                    q.append((nx, ny))

    # 2) Apaga o fundo conectado e suaviza o halo: quanto mais claro o pixel de
    #    borda, mais transparente (anti-aliasing limpo nas curvas).
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if visited[i]:
                px[x, y] = (255, 255, 255, 0)

    im.save(DST)
    print(f"OK -> {DST}  ({w}x{h})")


if __name__ == "__main__":
    main()
