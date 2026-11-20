"""Sessões aleatórias no navegador (Chromium e WebKit, computador e celular): digitar valor ou limite, mexer nas parcelas, trocar de aba, clicar nas barras e digitar lixo.

A cada passo confere parcela, total, valor recebido, IOF, juros, CET, "cada R$ 1" e a rosca contra calculo.py. Reaproveita o servidor e as simulações de testar_navegador.py.
Uso: python testar_aleatorio.py [sessoes] [passos]   (padrão: 6 sessões de 40 passos por navegador e tamanho de tela)
"""
import random
import sys
import threading

from playwright.sync_api import sync_playwright

import calculo
import testar_navegador as t

LIM = {"valor": (calculo.VALOR_MIN, calculo.VALOR_MAX), "limite": (300, 8000)}


def clamp(v, a, b):
    return min(b, max(a, v))


def sessao(pg, rnd, passos, tag):
    est = {"modo": "valor", "valor": 1000.0, "limite": 2000.0, "n": 12}
    pg.goto(t.BASE + "/")
    pg.wait_for_selector("#barras .pz")
    for i in range(passos):
        acao = rnd.choice(["digitar", "digitar", "parcelas", "aba", "barra", "lixo", "baixo"])
        if acao == "digitar":
            v = rnd.choice([rnd.randint(300, 5000), round(rnd.uniform(300, 5000), 2), rnd.randint(1, 20000)])
            pg.fill("#campo-valor", str(v).replace(".", ",")); pg.press("#campo-valor", "Enter")
            lo, hi = LIM[est["modo"]]
            est[est["modo"]] = clamp(float(v), lo, hi)
            desc = "digitar " + str(v)
        elif acao == "parcelas":
            n = rnd.randint(2, 12)
            pg.fill("#range-parcelas", str(n)); est["n"] = n
            desc = "parcelas " + str(n)
        elif acao == "aba":
            est["modo"] = "limite" if est["modo"] == "valor" else "valor"
            pg.click("#btn-modo-" + est["modo"])
            desc = "aba " + est["modo"]
        elif acao == "barra":
            n = rnd.randint(2, 12)
            pg.click("#barras .pz >> nth=" + str(n - 2)); est["n"] = n
            desc = "barra " + str(n)
        elif acao == "lixo":
            lixo = rnd.choice(["abc", "", "R$", "--", "1e9x"])
            pg.fill("#campo-valor", lixo); pg.press("#campo-valor", "Enter")
            if lixo == "1e9x":  # a página só lê os dígitos: "19", que fica abaixo do mínimo e vira o mínimo da faixa
                lo, hi = LIM[est["modo"]]
                est[est["modo"]] = float(clamp(19, lo, hi))
            desc = "lixo " + repr(lixo)
        else:  # valor abaixo do mínimo: o campo volta para o mínimo da faixa
            pg.fill("#campo-valor", str(rnd.randint(1, 250))); pg.press("#campo-valor", "Enter")
            lo, hi = LIM[est["modo"]]
            est[est["modo"]] = float(lo) if est["modo"] == "valor" else est[est["modo"]]
            desc = "baixo"
            # no modo limite, valores de 1 a 250 são menores que o mínimo (300) e a página os ignora ao digitar; ao sair do campo aplica o mínimo
            if est["modo"] == "limite":
                est["limite"] = 300.0
        r = calculo.simular(est["modo"], est["valor"], est["limite"], est["n"])
        abaixo = est["modo"] == "limite" and r["receber"] < calculo.VALOR_MIN
        passo = tag + "passo " + str(i + 1) + " (" + desc + "): "
        ok = (abs(t.numero(pg.inner_text("#r-parcela")) - round(r["parcela"], 2)) < 0.011 and abs(t.numero(pg.inner_text("#r-total")) - round(r["total"], 2)) < 0.011
              and abs(t.numero(pg.inner_text("#r-receber")) - round(r["receber"], 2)) < 0.011 and abs(t.numero(pg.inner_text("#r-iof")) - round(r["iof"], 2)) < 0.011
              and t.sem_nbsp(pg.inner_text("#r-juros")) == t.conteudo.pct(r["jurosMes"]) and t.sem_nbsp(pg.inner_text("#r-cet")) == t.conteudo.pct(r["cetAno"])
              and pg.text_content("#rosca-pct") == str(round((r["total"] - r["receber"]) / r["total"] * 100)) + "%"
              and pg.is_visible("#aviso-minimo") == abaixo and pg.is_disabled("#btn-cta") == abaixo)
        t.TOTAL[0] += 1
        if not ok:
            t.FALHAS.append(passo)
            print("FALHOU " + passo + str(est) + " parcela=" + pg.inner_text("#r-parcela") + " total=" + pg.inner_text("#r-total"))
    t.sem_rolagem_lateral(pg, tag + "fim: ")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sessoes = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    passos = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    httpd = t.ServidorThreads(("127.0.0.1", t.PORTA), t.Servidor)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    with sync_playwright() as pw:
        for nome, tipo in (("chromium", pw.chromium), ("webkit", pw.webkit)):
            nav = tipo.launch()
            for largura in (1280, 390):
                ctx, pg = t.nova_pagina(nav, largura)
                for s in range(sessoes):
                    sessao(pg, random.Random(1000 * largura + s), passos, nome + "/" + str(largura) + "/sessão " + str(s + 1) + ": ")
                erros = [e for e in pg.__dict__["_erros"] if "cloudflareinsights" not in e]
                t.confere(nome + "/" + str(largura) + ": sem erro de console", not erros, erros)
                ctx.close()
            nav.close()
    httpd.shutdown()
    print(str(t.TOTAL[0]) + " checagens, " + str(len(t.FALHAS)) + " falha(s)")
    sys.exit(1 if t.FALHAS else 0)


if __name__ == "__main__":
    main()
