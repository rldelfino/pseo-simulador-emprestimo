"""Pacote de publicação dos dados abertos em sites especializados (Kaggle, Hugging Face, dados.gov.br).

Por que existe: publicar o conjunto de dados onde analistas e jornalistas procuram dados gera links e citações reais, sem postar para ninguém e sem gastar.
O que depende de conta (login, token) fica pronto aqui, em publicacao/, e é gerado dos mesmos arquivos de paginas_seo/dados/, então se atualiza sozinho.
Nenhum segredo é escrito aqui: o usuário do Kaggle e os tokens ficam fora do repositório (variáveis de ambiente ou GitHub Secrets).

Cada conjunto mantém a licença da sua fonte: CC BY 4.0 para a Tabela 10 e ODbL 1.0 para as séries do Banco Central (que exige a mesma licença).

Rodar: python publicacao.py   (depois de python gerador_emprestimo.py)
"""
import json
import os
import shutil
import sys

import dados_abertos as da
import taxas_referencia as tr

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(AQUI, "paginas_seo", "dados")
PASTA_SAIDA = os.path.join(AQUI, "publicacao")
USUARIO_KAGGLE = "rodolfodelfino"  # usuário público do Kaggle (aparece na URL dos datasets); o token NÃO fica aqui

KAGGLE = {
    da.PIX["nome"]: dict(
        slug="pix-no-carto-parcela-iof-e-cet-tabela-10", titulo="Pix no cartão: parcela, IOF e CET (Tabela 10)",
        subtitulo="Custo do Pix no cartão de 2x a 12x para cada R$ 1.000, conferido toda semana",
        keywords=["finance", "brazil", "credit card", "interest rates", "installments"], licenca="CC-BY-4.0", hf_licenca="cc-by-4.0"),
    da.BCB["nome"]: dict(
        slug="taxas-mdias-de-crdito-pf-do-banco-central", titulo="Taxas médias de crédito PF do Banco Central",
        subtitulo="Juros médios do BC: cheque especial, pessoal não consignado e rotativo",
        keywords=["finance", "brazil", "banking", "interest rates", "central bank"], licenca="ODbL-1.0", hf_licenca="odbl"),
}


def _escrever(caminho, texto):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def _conjunto(nome):
    return next(c for c in da.CONJUNTOS if c["nome"] == nome)


def gerar(pasta_dados=PASTA_DADOS, pasta_saida=PASTA_SAIDA, usuario=USUARIO_KAGGLE):
    shutil.rmtree(pasta_saida, ignore_errors=True)
    resumo = {}
    for nome, k in KAGGLE.items():
        c = _conjunto(nome)
        csv_origem = os.path.join(pasta_dados, nome + ".csv")
        linhas = sum(1 for _ in open(csv_origem, encoding="utf-8")) - 1
        resumo[nome] = linhas
        descricao = c["descricao"] + "\n\n" + da.texto_licenca(c) + "\nComo citar: " + da.CITACAO + ". Atualizado toda semana."
        meta = {
            "title": k["titulo"], "id": usuario + "/" + k["slug"], "subtitle": k["subtitulo"], "description": descricao,
            "licenses": [{"name": k["licenca"]}], "keywords": k["keywords"],
            "resources": [{"path": nome + ".csv", "description": "; ".join(n for n, _, _ in c["colunas"])}],
        }
        _escrever(os.path.join(pasta_saida, "kaggle", nome, "dataset-metadata.json"), json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        shutil.copy(csv_origem, os.path.join(pasta_saida, "kaggle", nome, nome + ".csv"))

        card = ("---\nlicense: " + k["hf_licenca"] + "\nlanguage:\n- pt\npretty_name: " + json.dumps(k["titulo"], ensure_ascii=False) + "\nsize_categories:\n- n<1K\nconfigs:\n- config_name: default\n  data_files: " + nome + ".csv\ntags:\n"
                + "".join("- " + json.dumps(t, ensure_ascii=False) + "\n" for t in k["keywords"]) + "---\n\n# " + c["titulo"] + "\n\n" + c["descricao"] + "\n\n## Colunas\n"
                + "".join("- `" + n + "` (" + t + "): " + d + "\n" for n, t, d in c["colunas"])
                + "\n## Licença e fonte\n" + da.texto_licenca(c) + "\n\nFonte: " + c["fonte"]["title"] + " (" + c["fonte"]["path"] + ").\n")
        _escrever(os.path.join(pasta_saida, "huggingface", nome, "README.md"), card)
        shutil.copy(csv_origem, os.path.join(pasta_saida, "huggingface", nome, nome + ".csv"))

    ref = tr.mes_extenso(max(r["mes"] for r in tr.ler()))
    gov = "# Cadastro no dados.gov.br\n\nCampos para copiar (\"Cadastrar conjunto de dados\"). Os recursos entram por link, sem upload.\n"
    for c in da.CONJUNTOS:
        gov += ("\n## " + c["titulo"] + "\n\n- **Descrição:** " + c["descricao"] + "\n- **Publicador:** Datalab Global (Satori Soluções Comerciais LTDA, CNPJ 63.998.502/0001-73)\n"
                "- **Licença:** " + c["licenca"]["titulo"] + "\n- **Frequência:** semanal\n- **Recursos:**\n"
                "  - CSV: " + da.DOMINIO + "/dados/" + c["nome"] + ".csv\n  - JSON: " + da.DOMINIO + "/dados/" + c["nome"] + ".json\n"
                "  - Data package: " + da.DOMINIO + "/dados/datapackage-" + c["nome"] + ".json\n- **Fonte original:** " + c["fonte"]["path"] + "\n")
    gov += "\nDados do Banco Central até " + ref + ".\n"
    _escrever(os.path.join(pasta_saida, "dados-gov-br", "cadastro.md"), gov)

    leia = ("# Publicação dos dados abertos\n\nGerada por `publicacao.py`. Dois conjuntos, cada um com a licença da sua fonte (CC BY 4.0 e ODbL 1.0).\n\n"
            "1. **Kaggle:** os dois datasets já foram criados em 14/11/2026 (veja os links em `/dados-abertos`). Para atualizar, rode `kaggle datasets version -p publicacao/kaggle/<pasta> -m \"atualização semanal\"` com o token em variável de ambiente (`KAGGLE_API_TOKEN` ou `KAGGLE_KEY`), NUNCA no repositório. O título tem no máximo 50 caracteres e o subtítulo no máximo 80 (limites do Kaggle).\n"
            "2. **Hugging Face:** crie um dataset por pasta de `huggingface/` e envie o `README.md` e o CSV. O token fica fora do repositório.\n"
            "3. **dados.gov.br:** copie os campos de `dados-gov-br/cadastro.md`.\n")
    _escrever(os.path.join(pasta_saida, "LEIA-ME.md"), leia)
    return resumo


if __name__ == "__main__":
    r = gerar()
    print("publicacao/: " + "; ".join(n + " (" + str(l) + " linhas)" for n, l in r.items()))
    sys.exit(0)
