"""Avisa o Bing (e os demais buscadores que adotam o IndexNow) das URLs do sitemap depois de cada atualização.

O arquivo paginas_seo/<chave>.txt, com a chave dentro, prova que o site é nosso. A chave do IndexNow é PÚBLICA por desenho (fica
publicada em https://emprestimo.datalabglobal.com/<chave>.txt); não é segredo. O Google não usa IndexNow.

Só envia se o site já estiver no ar (a chave precisa responder no endereço). Se não estiver, avisa e sai com 0.
Falha de rede ou de HTTP NÃO derruba o pipeline: avisa e sai com 0.

Uso: python indexnow.py [caminho_do_sitemap] [--espera SEGUNDOS]
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request

HOST = "emprestimo.datalabglobal.com"
CHAVE = "1402751d110047b584ffbd74c6d00b6c"
LOCAL_DA_CHAVE = "https://" + HOST + "/" + CHAVE + ".txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
TAMANHO_LOTE = 10000


def urls_do_sitemap(caminho="paginas_seo/sitemap.xml"):
    with open(caminho, encoding="utf-8") as f:
        urls = re.findall(r"<loc>([^<]+)</loc>", f.read())
    return [u for u in urls if u.startswith("https://" + HOST + "/")]


def montar_payload(urls):
    return {"host": HOST, "key": CHAVE, "keyLocation": LOCAL_DA_CHAVE, "urlList": list(urls)}


def enviar(payload, endpoint=ENDPOINT):
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status


def site_no_ar(abrir=urllib.request.urlopen):
    """True se a chave responde no endereço público com o conteúdo certo."""
    try:
        req = urllib.request.Request(LOCAL_DA_CHAVE, headers={"User-Agent": "datalab-indexnow/1.0"})
        with abrir(req, timeout=30) as resp:
            return resp.status == 200 and resp.read().decode("utf-8").strip() == CHAVE
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def main(caminho="paginas_seo/sitemap.xml", espera=0, abrir=urllib.request.urlopen, enviar_fn=enviar, dormir=time.sleep):
    urls = urls_do_sitemap(caminho)
    if not urls:
        print("AVISO IndexNow: nenhuma URL no sitemap; nada a enviar")
        return 0
    if not site_no_ar(abrir):
        print("AVISO IndexNow: o site ainda não está no ar em " + LOCAL_DA_CHAVE + "; nada enviado")
        return 0
    if espera:
        dormir(espera)  # deixa o deploy do push terminar antes de avisar
    for i in range(0, len(urls), TAMANHO_LOTE):
        lote = urls[i:i + TAMANHO_LOTE]
        try:
            status = enviar_fn(montar_payload(lote))
            print("OK IndexNow: %d URL(s) enviadas (HTTP %s)" % (len(lote), status))
        except urllib.error.HTTPError as e:
            print("AVISO IndexNow: HTTP %s ao enviar %d URL(s) (%s)" % (e.code, len(lote), e.reason))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print("AVISO IndexNow: falha de rede (%s); segue sem avisar o Bing" % e)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    espera_s = 0
    if "--espera" in args:
        i = args.index("--espera")
        espera_s = int(args[i + 1])
        del args[i:i + 2]
    sys.exit(main(*(args[:1] or ["paginas_seo/sitemap.xml"]), espera=espera_s))
