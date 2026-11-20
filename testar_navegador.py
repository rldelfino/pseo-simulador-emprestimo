"""Teste de ponta a ponta no navegador (Chromium e WebKit, computador e celular): abre o site gerado e usa o simulador como uma pessoa usaria.

Precisa do Playwright (fora do CI). Sobe um servidor local em paginas_seo/ que aplica o _headers (CSP etc.) e o _redirects (301) como o Cloudflare Pages,
substitui o Umami e a API do parceiro por simulações (nenhum evento de teste vai ao Umami e nenhum pedido vai ao parceiro) e confere os números contra calculo.py.
Uso: python testar_navegador.py [--externos]   (--externos confere também os links para outros sites, com requisições GET simples)
"""
import http.server
import json
import os
import re
import socketserver
import sys
import threading
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

import calculo
import conteudo

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(AQUI, "paginas_seo")
PORTA = 8812
BASE = "http://127.0.0.1:" + str(PORTA)
FALHAS = []
TOTAL = [0]
UUID_TESTE = "UUID-DE-TESTE"


def confere(nome, cond, detalhe=""):
    TOTAL[0] += 1
    print(("OK    " if cond else "FALHOU") + " " + nome + (" -> " + str(detalhe) if not cond or detalhe else ""))
    if not cond:
        FALHAS.append(nome)


# ---------- servidor local que imita o Cloudflare Pages (headers e redirects) ----------

def _ler_headers():
    blocos, atual = {}, None
    for linha in open(os.path.join(PASTA, "_headers"), encoding="utf-8").read().splitlines():
        if not linha.strip():
            continue
        if not linha.startswith(" "):
            atual = linha.strip()
            blocos[atual] = {}
        else:
            k, v = linha.strip().split(":", 1)
            blocos[atual][k.strip()] = v.strip()
    return blocos


def _ler_redirects():
    saida = {}
    for linha in open(os.path.join(PASTA, "_redirects"), encoding="utf-8").read().splitlines():
        if linha.startswith("#") or not linha.strip():
            continue
        de, para, codigo = linha.split()
        saida[de] = (para, int(codigo))
    return saida


HEADERS = _ler_headers()
REDIRECTS = _ler_redirects()


class Servidor(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=PASTA, **k)

    def log_message(self, *a):
        pass

    def _cabecalhos(self):
        for k, v in HEADERS.get("/*", {}).items():
            if k == "Content-Security-Policy":
                v = v.replace("; upgrade-insecure-requests", "")  # em http://localhost o upgrade quebraria os próprios arquivos
            self.send_header(k, v)

    def send_head(self):
        caminho = self.path.split("?")[0].split("#")[0]
        if caminho in REDIRECTS:
            self.send_response(REDIRECTS[caminho][1])
            self.send_header("Location", REDIRECTS[caminho][0])
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        arquivo = os.path.join(PASTA, caminho.lstrip("/"))
        if caminho != "/" and not os.path.exists(arquivo) and os.path.exists(arquivo + ".html"):
            self.path = caminho + ".html"  # o Cloudflare serve /pagina como /pagina.html
        return super().send_head()

    def end_headers(self):
        self._cabecalhos()
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.exists(os.path.join(PASTA, "404.html")):
            corpo = open(os.path.join(PASTA, "404.html"), "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return
        super().send_error(code, message, explain)


class ServidorThreads(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


# ---------- ajudantes ----------

def numero(texto):
    return round(float(re.sub(r"[^\d,]", "", texto).replace(",", ".")), 2)


def sem_nbsp(texto):
    return texto.replace(" ", " ").replace(chr(160), " ")


def esperado(modo, valor, limite, n):
    return calculo.simular(modo, valor, limite, n)


def conferir_resultado(pg, tag, modo, valor, limite, n):
    r = esperado(modo, valor, limite, n)
    custo = r["total"] - r["receber"]
    confere(tag + "parcela", abs(numero(pg.inner_text("#r-parcela")) - round(r["parcela"], 2)) < 0.011, pg.inner_text("#r-parcela"))
    confere(tag + "total", abs(numero(pg.inner_text("#r-total")) - round(r["total"], 2)) < 0.011, pg.inner_text("#r-total"))
    confere(tag + "recebe", abs(numero(pg.inner_text("#r-receber")) - round(r["receber"], 2)) < 0.011, pg.inner_text("#r-receber"))
    confere(tag + "IOF", abs(numero(pg.inner_text("#r-iof")) - round(r["iof"], 2)) < 0.011, pg.inner_text("#r-iof"))
    confere(tag + "juros ao mês", sem_nbsp(pg.inner_text("#r-juros")) == conteudo.pct(r["jurosMes"]), pg.inner_text("#r-juros"))
    confere(tag + "CET ao ano", sem_nbsp(pg.inner_text("#r-cet")) == conteudo.pct(r["cetAno"]), pg.inner_text("#r-cet"))
    confere(tag + "cada R$ 1", abs(numero(pg.inner_text("#k-real")) - round(r["total"] / r["receber"], 2)) < 0.011, pg.inner_text("#k-real"))
    confere(tag + "% de juros e IOF na rosca", pg.text_content("#rosca-pct") == str(round(custo / r["total"] * 100)) + "%", pg.text_content("#rosca-pct"))
    return r


def sem_rolagem_lateral(pg, tag):
    larg = pg.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    confere(tag + "sem rolagem lateral", larg[0] <= larg[1], larg)


def nova_pagina(nav, largura, altura=900):
    ctx = nav.new_context(viewport={"width": largura, "height": altura}, device_scale_factor=1)
    pg = ctx.new_page()
    erros = []
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: erros.append("PAGEERROR " + str(e)))
    # Umami e API do parceiro simulados: nada de teste sai da máquina
    pg.route("**/cloud.umami.is/**", lambda r: r.fulfill(status=200, content_type="application/javascript", body=""))
    pg.add_init_script("window.umami={track:function(n,d){window.__ev=(window.__ev||[]);window.__ev.push([n,d]);}}")
    pg.__dict__["_erros"] = erros
    return ctx, pg


def rotas_parceiro(pg, modo="ok"):
    chamadas = []

    def api(r):
        chamadas.append(json.loads(r.request.post_data or "{}"))
        if r.request.method == "OPTIONS":
            r.fulfill(status=204, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type"})
        elif modo == "ok":
            r.fulfill(status=200, content_type="application/json", headers={"Access-Control-Allow-Origin": "*"}, body=json.dumps({"uuid": UUID_TESTE}))
        else:
            r.fulfill(status=500, content_type="application/json", headers={"Access-Control-Allow-Origin": "*"}, body="{}")

    pg.route("https://api.triagem.digital/**", api)
    pg.route("https://checkoutonline.digital/**", lambda r: r.fulfill(status=200, content_type="text/html", body="<html><body>parceiro (simulado)</body></html>"))
    return chamadas


def eventos(pg):
    return [e[0] for e in (pg.evaluate("window.__ev || []") or [])]


# ---------- cenários ----------

def rodar(nav, nome_nav, largura):
    tag = nome_nav + "/" + str(largura) + ": "
    ctx, pg = nova_pagina(nav, largura)
    chamadas = rotas_parceiro(pg)
    celular = largura < 700

    pg.goto(BASE + "/")
    pg.wait_for_selector("#barras .pz")
    sem_rolagem_lateral(pg, tag + "home: ")
    r = conferir_resultado(pg, tag + "inicial R$ 1.000 em 12x: ", "valor", 1000, 0, 12)
    confere(tag + "título da página", pg.title() == "Empréstimo pessoal com crédito do cartão: parcela e IOF", pg.title())
    confere(tag + "h1 com o nome do produto", "Empréstimo pessoal com crédito do cartão" in pg.inner_text("h1"), pg.inner_text("h1"))
    confere(tag + "nota do limite", "comprometido no limite" in pg.inner_text("#nota-limite"), pg.inner_text("#nota-limite"))
    confere(tag + "preenchimento do slider (data-p)", pg.get_attribute("#range-parcelas", "data-p") == "100" and pg.get_attribute("#range-valor", "data-p") == "15")
    if not celular:
        confere(tag + "barra de resumo some no computador", not pg.is_visible("#barra-resumo"))

    # valor digitado e parcelas pelo controle deslizante
    pg.fill("#campo-valor", "2.500"); pg.press("#campo-valor", "Enter")
    pg.fill("#range-parcelas", "6")
    conferir_resultado(pg, tag + "R$ 2.500 em 6x: ", "valor", 2500, 0, 6)
    confere(tag + "slider de parcelas atualiza data-p", pg.get_attribute("#range-parcelas", "data-p") == "40", pg.get_attribute("#range-parcelas", "data-p"))
    confere(tag + "tabela de prazos: 11 linhas e a atual marcada", pg.locator("#corpo-prazos tr").count() == 11 and pg.locator("#corpo-prazos tr[aria-current]").count() == 1)
    pg.click("#detalhe-prazos summary")
    confere(tag + "tabela de prazos abre", pg.is_visible("#corpo-prazos"))
    sem_rolagem_lateral(pg, tag + "tabela de prazos aberta: ")

    # barra do prazo
    pg.click("#barras .pz >> nth=10")  # 12x
    confere(tag + "barra de 12x muda o prazo", pg.inner_text("#txt-parcelas") == "12x" and pg.get_attribute("#range-parcelas", "data-p") == "100")
    conferir_resultado(pg, tag + "R$ 2.500 em 12x (pela barra): ", "valor", 2500, 0, 12)

    # endereço compartilhável: grava e lê
    pg.wait_for_timeout(700)
    confere(tag + "endereço da simulação", "modo=valor" in pg.url and "valor=2500" in pg.url and "parcelas=12" in pg.url, pg.url)
    pg.goto(BASE + "/?modo=limite&limite=3000&parcelas=9")
    pg.wait_for_selector("#barras .pz")
    conferir_resultado(pg, tag + "link compartilhado (limite R$ 3.000 em 9x): ", "limite", 0, 3000, 9)
    confere(tag + "aba 'Usar meu limite' selecionada", pg.get_attribute("#btn-modo-limite", "aria-selected") == "true")
    pg.goto(BASE + "/?modo=valor&valor=<script>&parcelas=99&prop=abc")
    pg.wait_for_selector("#barras .pz")
    conferir_resultado(pg, tag + "endereço com lixo vira o padrão: ", "valor", 1000, 0, 12)

    # modo limite: abaixo do mínimo
    pg.click("#btn-modo-limite")
    pg.fill("#campo-valor", "400"); pg.press("#campo-valor", "Enter")
    confere(tag + "limite baixo avisa o mínimo e trava o botão", pg.is_visible("#aviso-minimo") and pg.is_disabled("#btn-cta") and "limite de pelo menos" in pg.inner_text("#aviso-minimo"), pg.inner_text("#aviso-minimo"))
    pg.fill("#campo-valor", "2.000"); pg.press("#campo-valor", "Enter")
    pg.fill("#range-parcelas", "12")
    conferir_resultado(pg, tag + "limite R$ 2.000 em 12x: ", "limite", 0, 2000, 12)
    confere(tag + "limite normal destrava o botão", not pg.is_disabled("#btn-cta") and not pg.is_visible("#aviso-minimo"))
    pg.click("#btn-modo-valor")

    # compara com o BCB
    confere(tag + "bloco do BCB com 4 linhas", pg.locator("#ref-lista li").count() == 4 and "Empréstimo com crédito do cartão em 12x" in pg.inner_text("#ref-lista"), pg.inner_text("#ref-lista"))

    # já tem uma proposta?
    pg.fill("#campo-valor", "1.000"); pg.press("#campo-valor", "Enter")
    pg.fill("#range-parcelas", "12")
    pg.click("#det-prop summary")
    confere(tag + "campo da proposta abre", pg.is_visible("#campo-prop"))
    pg.fill("#campo-prop", "140")
    taxa = calculo.taxa_implicita(1000, 140, 12)
    txt = sem_nbsp(pg.inner_text("#msg-prop"))
    confere(tag + "taxa da proposta (mais cara que a Tabela 10)", conteudo.pct(taxa) in txt and "Tabela 10" in txt and "R$ 96,10 a mais no total" in txt, txt)
    pg.fill("#campo-prop", "120")
    txt = sem_nbsp(pg.inner_text("#msg-prop"))
    confere(tag + "taxa da proposta (mais barata que a Tabela 10)", conteudo.pct(calculo.taxa_implicita(1000, 120, 12)) in txt and "R$ 143,90 a menos no total" in txt, txt)
    pg.fill("#campo-prop", "140")
    pg.fill("#campo-prop", "70")
    confere(tag + "parcela que não cobre o valor avisa", "pagaria menos do que recebe" in pg.inner_text("#msg-prop"), pg.inner_text("#msg-prop"))
    pg.fill("#campo-prop", "")
    confere(tag + "sem parcela volta o texto padrão", "Informe a parcela" in pg.inner_text("#msg-prop"))
    pg.fill("#campo-prop", "140")
    pg.wait_for_timeout(700)
    confere(tag + "parcela da proposta no endereço", "prop=140" in pg.url, pg.url)
    pg.fill("#campo-prop", "")

    # tela de confirmação antes do parceiro
    pg.fill("#campo-valor", "1.000"); pg.press("#campo-valor", "Enter")
    confere(tag + "diálogo começa fechado", not pg.is_visible("#dlg-confirma"))
    pg.click("#btn-cta")
    confere(tag + "botão abre a tela de confirmação", pg.is_visible("#dlg-confirma"))
    confere(tag + "confirmação com o resumo e o aviso do pedido real", "R$ 1.583,90" in sem_nbsp(pg.inner_text("#dlg-resumo")) and "6 passos" in pg.inner_text("#dlg-confirma") and "limite do seu cartão" in pg.inner_text("#dlg-confirma"), pg.inner_text("#dlg-resumo"))
    confere(tag + "nada foi enviado ao parceiro só por abrir a confirmação", len(chamadas) == 0)
    pg.click("#btn-voltar")
    confere(tag + "voltar e ajustar fecha", not pg.is_visible("#dlg-confirma"))
    pg.click("#btn-cta"); pg.keyboard.press("Escape")
    confere(tag + "Esc fecha a confirmação", not pg.is_visible("#dlg-confirma"))
    pg.click("#btn-cta")
    pg.click("#btn-parceiro")
    pg.wait_for_url("https://checkoutonline.digital/**", timeout=15000)
    confere(tag + "continuar leva ao parceiro com o código da simulação", pg.url.startswith("https://checkoutonline.digital/?l=" + calculo.TABELA["table_uuid"]) and pg.url.endswith("&s=" + UUID_TESTE), pg.url)
    confere(tag + "só valor e prazo foram ao parceiro", chamadas and chamadas[-1] == {"parcels": 12, "tableUUID": calculo.TABELA["table_uuid"], "desiredValue": 1000}, chamadas)

    # eventos e falha da API do parceiro
    pg.goto(BASE + "/?modo=valor&valor=1000&parcelas=12")
    pg.wait_for_selector("#barras .pz")
    pg.unroute("https://api.triagem.digital/**")
    chamadas2 = rotas_parceiro(pg, "falha")
    pg.fill("#range-parcelas", "10")
    pg.click("#btn-cta")
    pg.click("#btn-parceiro")
    pg.wait_for_selector("#aviso-proposta:not([hidden])")
    confere(tag + "API fora: avisa e oferece continuar mesmo assim", "Não conseguimos pré-preencher" in pg.inner_text("#aviso-proposta") and
            (pg.get_attribute("#link-parceiro", "href") or "").startswith("https://checkoutonline.digital/?l=" + calculo.TABELA["table_uuid"]), pg.inner_text("#aviso-proposta"))
    confere(tag + "API fora: botão volta a funcionar", not pg.is_disabled("#btn-parceiro") and pg.url.startswith(BASE))
    nomes = eventos(pg)
    for e in ("usou-simulador-emprestimo", "abriu-confirmacao", "cta-parceiro", "cta-parceiro-sem-preenchimento"):
        confere(tag + "evento " + e, e in nomes, nomes)
    confere(tag + "nenhum evento com nome antigo", not [n for n in nomes if n.endswith("-pix")], nomes)

    # copiar o link
    pg.keyboard.press("Escape")
    pg.click("#btn-copiar")
    pg.wait_for_selector("#msg-copiado:not(:empty)")
    confere(tag + "copiar o link responde", "Link copiado" in pg.inner_text("#msg-copiado") or "Não deu para copiar" in pg.inner_text("#msg-copiado"), pg.inner_text("#msg-copiado"))

    # voltar à simulação a partir de uma página interna
    pg.goto(BASE + "/?modo=valor&valor=1800&parcelas=7")
    pg.wait_for_selector("#barras .pz")
    pg.wait_for_timeout(500)
    pg.goto(BASE + "/como-funciona")
    href = pg.get_attribute("a[data-volta] >> nth=0", "href")
    confere(tag + "voltar à simulação guarda a última simulação", href and "valor=1800" in href and "parcelas=7" in href, href)
    confere(tag + "guia com o nome certo", "empréstimo pessoal com crédito do cartão" in pg.inner_text("h1").lower())
    sem_rolagem_lateral(pg, tag + "guia: ")

    # páginas internas: sem rolagem lateral, sem erro, tabelas legíveis
    for slug in [p["slug"] for p in conteudo.PAGINAS]:
        pg.goto(BASE + "/" + slug)
        sem_rolagem_lateral(pg, tag + "/" + slug + ": ")
    # menu do celular
    if celular:
        pg.goto(BASE + "/")
        pg.click("header details summary")
        confere(tag + "menu do celular abre e tem os guias", pg.is_visible("header details nav") and pg.locator("header details nav a").count() >= 8)
        pg.keyboard.press("Escape")
        confere(tag + "Esc fecha o menu", not pg.is_visible("header details nav"))
        # barra fixa de resumo: aparece com o simulador na tela e o resultado fora
        pg.set_viewport_size({"width": largura, "height": 560})  # tela baixa: com o simulador à vista, o resultado fica fora
        pg.goto(BASE + "/")
        pg.wait_for_selector("#barras .pz")
        pg.evaluate("document.getElementById('simulador').scrollIntoView()")
        pg.wait_for_timeout(300)
        pg.evaluate("window.scrollBy(0, 120)")
        pg.wait_for_timeout(400)
        confere(tag + "barra de resumo aparece no celular", pg.is_visible("#barra-resumo") and "x de" in pg.inner_text("#resumo-parcela"), pg.inner_text("#resumo-parcela"))

    # erros de console (o beacon do Cloudflare só existe em produção)
    erros = [e for e in pg.__dict__["_erros"] if "cloudflareinsights" not in e and "status of 500" not in e]  # o 500 é a falha da API do parceiro simulada de propósito
    confere(tag + "sem erro de console", not erros, erros)
    ctx.close()


def links_internos_e_redirects():
    def pedir(caminho, seguir=False):
        class SemRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        op = urllib.request.build_opener(urllib.request.HTTPRedirectHandler if seguir else SemRedirect)
        try:
            r = op.open(BASE + caminho, timeout=10)
            return r.status, r.headers
        except urllib.error.HTTPError as e:
            return e.code, e.headers

    vistos, quebrados = set(), []
    paginas = ["/"] + ["/" + p["slug"] for p in conteudo.PAGINAS]
    for pagina in paginas:
        html = urllib.request.urlopen(BASE + pagina).read().decode("utf-8")
        for href in re.findall(r'href="(/[^"#?]*)', html) + re.findall(r'src="(/[^"?]*)', html):
            if href in vistos:
                continue
            vistos.add(href)
            if pedir(href)[0] != 200:
                quebrados.append((pagina, href))
    confere("links e arquivos internos: " + str(len(vistos)) + " sem 404", not quebrados, quebrados)
    st, h = pedir("/pix-no-cartao-ou-outro-credito")
    confere("301 do slug antigo para o novo", st == 301 and h.get("Location") == "/emprestimo-com-cartao-ou-outro-credito", (st, h.get("Location")))
    st, h = pedir("/pix-no-cartao-ou-outro-credito.html")
    confere("301 do slug antigo com .html", st == 301 and h.get("Location") == "/emprestimo-com-cartao-ou-outro-credito", (st, h.get("Location")))
    st, h = pedir("/dados/pix-no-cartao-tabela-10.csv")
    confere("301 do CSV antigo", st == 301 and h.get("Location") == "/dados/emprestimo-cartao-tabela-10.csv", (st, h.get("Location")))
    st, _ = pedir("/emprestimo-com-cartao-ou-outro-credito")
    confere("página nova responde 200", st == 200)
    st, _ = pedir("/yandex_90c15c3be650b0ed.html")
    confere("arquivo de verificação do Yandex responde 200", st == 200)
    st, _ = pedir("/nao-existe-xyz")
    confere("endereço inexistente dá 404", st == 404)
    st, h = pedir("/")
    csp = h.get("Content-Security-Policy", "")
    confere("cabeçalhos de segurança no HTML", all(h.get(k) for k in ("Strict-Transport-Security", "X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy", "Referrer-Policy")) and
            h.get("X-Frame-Options") == "DENY" and h.get("X-Content-Type-Options") == "nosniff" and "max-age=31536000" in h.get("Strict-Transport-Security", ""), dict(h))
    confere("CSP sem inline nem eval e com object-src none", "'unsafe-inline'" not in csp and "'unsafe-eval'" not in csp and "object-src 'none'" in csp and "frame-ancestors 'none'" in csp, csp)


def links_externos():
    html = ""
    for pagina in ["/"] + ["/" + p["slug"] for p in conteudo.PAGINAS]:
        html += urllib.request.urlopen(BASE + pagina).read().decode("utf-8")
    urls = sorted(set(re.findall(r'href="(https://[^"]+)"', html)))
    urls = [u for u in urls if "cloud.umami.is" not in u]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (verificacao de links)"})
            r = urllib.request.urlopen(req, timeout=25)
            confere("externo " + u, r.status == 200, r.status)
        except urllib.error.HTTPError as e:
            confere("externo " + u, e.code in (401, 403, 429), e.code)  # alguns sites barram robôs: não é link quebrado
        except Exception as e:  # noqa: BLE001
            confere("externo " + u, False, repr(e))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    httpd = ServidorThreads(("127.0.0.1", PORTA), Servidor)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    links_internos_e_redirects()
    if "--externos" in sys.argv:
        links_externos()
    with sync_playwright() as pw:
        for nome, tipo in (("chromium", pw.chromium), ("webkit", pw.webkit)):
            nav = tipo.launch()
            for largura in (1280, 390):
                rodar(nav, nome, largura)
            nav.close()
    httpd.shutdown()
    print("\n" + str(TOTAL[0]) + " checagens, " + str(len(FALHAS)) + " falha(s)")
    for f in FALHAS:
        print(" - " + f)
    sys.exit(1 if FALHAS else 0)


if __name__ == "__main__":
    main()
