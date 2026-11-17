"""Gera paginas_seo/og-image.png (1200x630) a partir de src/og-image.html, com os números de calculo.py.

Ferramenta manual (precisa do Playwright: pip install playwright && playwright install chromium); o CI não roda isto.
Depois, rode o gerador do site para atualizar a versão (?v=) da imagem nas páginas.
"""
import os
import sys

import calculo

AQUI = os.path.dirname(os.path.abspath(__file__))


def brl(v):
    return "R$ " + format(round(v, 2), ",.2f").replace(",", "#").replace(".", ",").replace("#", ".")


def pct(v):
    return format(round(v, 2), ",.2f").replace(",", "#").replace(".", ",").replace("#", ".") + "%"


def html_final(n=12, valor=1000):
    r = calculo.simular("valor", valor, 0, n)
    texto = open(os.path.join(AQUI, "src", "og-image.html"), encoding="utf-8").read()
    for chave, v in (("PIX", brl(r["pix"])), ("N", str(n)), ("TOTAL", brl(r["total"])), ("CET", pct(r["cetAno"]))):
        texto = texto.replace("@@" + chave + "@@", v)
    return texto


def main():
    from playwright.sync_api import sync_playwright
    temp = os.path.join(AQUI, "src", "_og-image-final.html")
    with open(temp, "w", encoding="utf-8") as f:
        f.write(html_final())
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1200, "height": 630})
            pg.goto("file:///" + temp.replace("\\", "/"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            pg.screenshot(path=os.path.join(AQUI, "paginas_seo", "og-image.png"))
            b.close()
    finally:
        os.remove(temp)
    print("og-image.png gerada")


if __name__ == "__main__":
    sys.exit(main())
