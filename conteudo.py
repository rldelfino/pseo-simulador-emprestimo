"""Conteúdo das páginas. Cada página tem texto próprio; nada de páginas quase iguais.

Nome do produto: "Empréstimo pessoal com crédito do cartão". É um empréstimo pessoal em que o limite do cartão de crédito é a fonte do dinheiro, entregue por Pix.
Nunca é "Pix no cartão", "Pix com cartão" nem "crédito por Pix": esses nomes induzem a erro e só aparecem (uma vez, na FAQ) para corrigir quem os procura.

Regras: nenhum número que não venha da Tabela 10 (calculo.py) ou de uma fonte citada; nenhum banco nem o nome do parceiro citados, nem ranking;
sem prometer aprovação. Os números dos textos são calculados aqui a partir de calculo.simular, para não divergirem do simulador.
Sem f-string aninhada (o CI roda Python 3.10).
"""
import calculo
import dados_abertos as da
import taxas_referencia as tr

GITHUB = "https://github.com/rldelfino/pseo-simulador-emprestimo"
NOME = "Empréstimo pessoal com crédito do cartão"

# ---------- helpers de formatação ----------


def brl(v):
    s = format(round(v + 1e-9, 2), ",.2f")
    return "R$ " + s.replace(",", "#").replace(".", ",").replace("#", ".")


def brl0(v):
    return "R$ " + format(round(v), ",d").replace(",", ".")


def pct(v):
    s = format(round(v, 2), ",.2f")
    return s.replace(",", "#").replace(".", ",").replace("#", ".") + "%"


# ---------- blocos de HTML (o estilo vem de src/estilo.css; sem atributo style) ----------


def h2(t):
    return "<h2>" + t + "</h2>\n"


def h3(t):
    return "<h3>" + t + "</h3>\n"


def p(t):
    return "<p>" + t + "</p>\n"


def ul(itens, classe=""):
    return "<ul" + (' class="' + classe + '"' if classe else "") + ">" + "".join("<li>" + i + "</li>" for i in itens) + "</ul>\n"


def ol(itens):
    return "<ol>" + "".join("<li>" + i + "</li>" for i in itens) + "</ol>\n"


def aviso(t, ok=False):
    return '<div class="aviso' + (" ok" if ok else "") + '">' + t + "</div>\n"


def a(href, texto):
    return '<a href="' + href + '">' + texto + "</a>"


def tabela(cabecalho, linhas, legenda):
    topo = "".join('<th scope="col">' + c + "</th>" for c in cabecalho)
    # data-l: rótulo da coluna, usado no celular (o CSS empilha cada linha em um cartão; sem rolagem lateral)
    corpo = "".join("<tr>" + "".join('<td data-l="' + cabecalho[i] + '">' + c + "</td>" for i, c in enumerate(l)) + "</tr>" for l in linhas)
    return '<div class="tw"><table><caption>' + legenda + "</caption><thead><tr>" + topo + "</tr></thead><tbody>" + corpo + "</tbody></table></div>\n"


def _r(n, valor=1000):
    return calculo.simular("valor", valor, 0, n)


# ---------- o que é (texto-base, repetido com variações nas páginas) ----------
O_QUE_E = ("É um empréstimo pessoal em que o limite do seu cartão de crédito é a fonte do dinheiro: você escolhe um valor, recebe por Pix na sua conta e "
           "paga em parcelas na fatura do cartão, com juros e IOF.")


def custo_home():
    """Frase da home sobre juros e CET, com os números calculados da Tabela 10 (nunca digitados à mão)."""
    r2, r12 = _r(2), _r(12)
    return ("Os juros vão de " + pct(r2["jurosMes"]) + " ao mês (2x) a " + pct(r12["jurosMes"]) + " ao mês (12x). O CET, que inclui o IOF e é contado ao ano, vai de "
            + pct(r2["cetAno"]) + " a " + pct(r12["cetAno"]) + ". Por isso o simulador mostra quanto você paga a mais antes do botão.")


# ---------- perguntas frequentes da home (também viram FAQPage) ----------
FAQ = [
    ("O que é o empréstimo pessoal com crédito do cartão?",
     O_QUE_E + " Não é compra parcelada nem um saque comum: é um contrato de empréstimo, com juros, IOF e CET informados antes de você aceitar."),
    ("O que acontece com o limite do cartão?",
     "O total que vai para as parcelas (o valor que você recebe mais juros e IOF) é lançado no limite do cartão: é por isso que o modo “Usar meu limite” "
     "calcula quanto você consegue receber a partir do limite que tem. Enquanto as parcelas não forem pagas, esse valor fica comprometido; como e quando o seu "
     "banco libera o limite conforme você paga é regra do emissor do cartão, então confirme com ele."),
    ("Quem pode solicitar?",
     "Segundo o parceiro, pessoa maior de 18 anos, com cartão de crédito ativo e com limite disponível, e conta bancária em seu nome. "
     "Essas condições são do parceiro e podem mudar."),
    ("Qual o valor mínimo e o máximo, e quantas parcelas?",
     "De R$ 300 a R$ 5.000, em 2 a 12 parcelas na fatura, sempre respeitando o limite do cartão."),
    ("Já vi isso chamado de “Pix no cartão”, “Pix parcelado” ou “saque do limite”. É a mesma coisa?",
     "Esses nomes aparecem em anúncios, mas induzem a erro. Não é um Pix pago com cartão nem um crédito por Pix, e “Pix parcelado” costuma ser outra coisa: "
     "parcelar uma compra paga por Pix. Aqui você recebe dinheiro de um empréstimo, e o Pix é só o jeito de ele chegar à sua conta. "
     "“Saque do limite” descreve o efeito, mas há contrato de empréstimo, com juros e IOF."),
    ("Como recebo o dinheiro?",
     "Por Pix, em uma chave em seu próprio nome. O parceiro não aceita chave de outra pessoa."),
    ("Como pago?",
     "Pelas parcelas lançadas na fatura do cartão, que você paga junto com o resto da fatura."),
    ("Estou negativado. Posso contratar?",
     "A aprovação depende da análise de crédito do parceiro. Não há garantia de aprovação nem de valor."),
    ("É seguro e legal?",
     "A operação é formalizada por Cédula de Crédito Bancário (Lei nº 10.931/2004, arts. 26 a 45-A) e feita por correspondente bancário, "
     "que segue as normas do Banco Central e do CMN. Segurança, porém, também depende de você: leia o guia "
     + a("/e-seguro-golpes", "É seguro? Como evitar golpes") + "."),
    ("A Datalab Global é o banco?",
     "Não. Este site é um simulador. Quem faz a operação é um parceiro (correspondente bancário). Veja " + a("/sobre", "Sobre") + "."),
]


# ---------- páginas ----------

def corpo_como_funciona(ctx):
    r2, r12 = _r(2), _r(12)
    return (
        p(O_QUE_E + " Esta página explica o caminho do pedido ao dinheiro na conta, com o que o próprio parceiro informa na tela de contratação.")
        + h2("Em resumo")
        + ul([
            "Você escolhe um valor entre R$ 300 e R$ 5.000 e um prazo de 2 a 12 parcelas.",
            "O parceiro analisa o seu crédito. Aprovando, o valor cai por Pix em uma chave em seu nome.",
            "O total (valor mais juros e IOF) é lançado no limite do seu cartão e dividido nas faturas, junto com o resto da fatura.",
            "É um crédito caro: para receber " + brl(1000) + ", você paga entre " + brl(r2["total"]) + " (2x) e " + brl(r12["total"]) + " (12x).",
        ])
        + h2("O que acontece com o limite do cartão")
        + p("O limite do cartão é a fonte do dinheiro. O total das parcelas é lançado nele, e por isso o simulador tem o modo “Usar meu limite”: você informa quanto tem "
            "disponível e ele calcula quanto consegue receber (o valor recebido é menor que o limite, porque os juros e o IOF também ocupam espaço). "
            "A forma como o seu banco libera o limite conforme você paga as parcelas é regra do emissor do cartão: confirme com ele antes de contratar.")
        + h2("Passo a passo")
        + ol([
            "<strong>Simule aqui.</strong> Escolha o valor que quer receber (ou o limite que tem no cartão) e o número de parcelas. O custo aparece na hora, antes de qualquer botão.",
            "<strong>Clique em Ver minha proposta.</strong> Uma tela de confirmação resume o que vai acontecer. Ao continuar, este site envia ao parceiro só o valor e o prazo da simulação, sem nenhum dado seu, e abre a tela de contratação no ambiente do parceiro.",
            "<strong>Identifique-se no ambiente do parceiro.</strong> A primeira tela pede CPF, data de nascimento e o documento que você vai usar (RG ou CNH), com a data de emissão. Esses dados vão para o parceiro, não para este site.",
            "<strong>Assine o contrato (CCB).</strong> O parceiro avisa que é preciso estar com o documento original em mãos: não aceita foto, cópia ou versão digital.",
            "<strong>Informe a chave Pix.</strong> Depois da aprovação, o valor só pode ser enviado para uma chave em seu próprio nome: o Pix é só o meio de o dinheiro chegar.",
            "<strong>Receba e pague na fatura.</strong> As parcelas aparecem nas próximas faturas do cartão.",
        ])
        + p("A tela de contratação do parceiro tem 6 passos. Descrevemos acima o que o parceiro informa logo na primeira tela; não temos como "
            "verificar, a cada dia, tudo o que acontece nos passos seguintes. As condições finais valem as que aparecem na tela do parceiro.")
        + h2("Computador ou celular?")
        + p("A contratação foi pensada para o celular. Se você abrir a proposta em um computador, o parceiro mostra um QR Code: aponte a câmera do celular "
            "e a proposta abre já preenchida com o valor e o prazo que você simulou.")
        + h2("O que ter em mãos")
        + ul([
            "Cartão de crédito em seu nome, com limite disponível.",
            "Documento com foto (RG ou CNH), original.",
            "Dados do seu endereço atual.",
            "Uma chave Pix em seu nome, só para receber o dinheiro.",
        ])
        + aviso("<strong>Antes de clicar:</strong> veja quanto isso custa em " + a("/custo-cet-iof", "CET e IOF: quanto custa de verdade")
                + " e se " + a("/quando-nao-vale-a-pena", "esta é uma boa ideia para o seu caso") + ".")
    )


def corpo_seguro(ctx):
    return (
        p("Golpes de crédito são comuns, e uma proposta de dinheiro rápido é o cenário preferido de quem aplica golpe. Esta página mostra "
          "o que checar antes de contratar qualquer crédito, e o que é específico do empréstimo com crédito do cartão.")
        + h2("O que é verificável aqui")
        + ul([
            "<strong>Quem é o responsável por este site:</strong> Satori Soluções Comerciais LTDA, CNPJ " + ctx["cnpj"] + " (marca Datalab Global). Você pode consultar o CNPJ no site da Receita Federal.",
            "<strong>Este site não pede dado pessoal.</strong> Você só informa valor e prazo. CPF, documento e dados do cartão são pedidos pelo parceiro, em outra tela.",
            "<strong>Contrato formal:</strong> a operação é formalizada por Cédula de Crédito Bancário (CCB, Lei nº 10.931/2004), com as condições registradas.",
            "<strong>Quem opera:</strong> um correspondente bancário, que atua por conta de uma instituição financeira e segue as normas do Banco Central e do CMN. Não verificamos, por você, o cadastro do parceiro: se quiser conferir, pergunte à instituição financeira responsável e peça o nome dela no contrato.",
            "<strong>Endereço da contratação:</strong> o botão do simulador leva ao ambiente do parceiro, que tem endereço próprio, diferente deste site, e mostra o nome da empresa na tela. Antes de digitar qualquer dado, confira o endereço na barra do navegador e compare com o que a tela de confirmação anunciou.",
        ])
        + h2("Sinais de golpe")
        + ul([
            "Pedem pagamento adiantado (taxa, seguro, depósito de garantia) para liberar o dinheiro. Neste empréstimo, você paga só as parcelas, na fatura.",
            "Mandam um link por WhatsApp, SMS ou e-mail e pedem que você digite dados do cartão ali. Comece sempre pelo site oficial e confira o endereço.",
            "Pedem a senha do cartão, códigos de verificação que chegam por SMS ou acesso remoto ao seu celular. Nenhuma instituição legítima precisa disso.",
            "Pedem que o Pix seja feito para a chave de outra pessoa. O parceiro só aceita chave em seu próprio nome.",
            "Prometem aprovação garantida. Crédito depende de análise; quem garante aprovação está mentindo.",
            "Têm pressa: &quot;só hoje&quot;, &quot;última vaga&quot;. Crédito sério dá tempo para ler o contrato.",
        ])
        + h2("Antes de assinar, confira na tela")
        + ul([
            "O valor que vai cair na sua conta e o total que vai para a fatura (e para o limite do cartão).",
            "O número e o valor das parcelas, o IOF, a taxa de juros e o custo efetivo total (CET).",
            "Se os números batem com a sua simulação. Se estiverem muito diferentes, não continue.",
        ])
        + h2("Se você caiu em um golpe")
        + ul([
            "Contate imediatamente o banco emissor do cartão e peça o bloqueio do cartão e a contestação.",
            "Se houve Pix, peça ao seu banco o acionamento do Mecanismo Especial de Devolução (MED).",
            "Registre um boletim de ocorrência e guarde conversas, comprovantes e endereços de site.",
        ])
        + aviso("Esta página é informativa e não substitui orientação jurídica. Para entender o custo, leia "
                + a("/custo-cet-iof", "CET e IOF") + "; para o passo a passo, " + a("/como-funciona", "Como funciona") + ".")
    )


def corpo_custo(ctx):
    linhas = []
    for n in calculo.PARCELAS:
        r = _r(n)
        linhas.append([str(n) + "x", brl(r["parcela"]), brl(r["total"]), brl(r["total"] - 1000), brl(r["iof"]), pct(r["jurosMes"]), pct(r["cetAno"])])
    r2, r3, r12 = _r(2), _r(3), _r(12)
    extra2, extra12 = r2["total"] - 1000, r12["total"] - 1000
    dif = extra12 - extra2
    return (
        p("Quando você recebe " + brl(1000) + " e parcela na fatura do cartão, o que você paga a mais se chama custo. Ele aparece em duas formas: "
          "o valor em reais e o CET, uma taxa que reúne tudo. Entender a diferença evita sustos.")
        + h2("O que é CET")
        + p("CET é o Custo Efetivo Total: soma os juros, os tributos (como o IOF) e outras despesas do contrato e expressa tudo em uma taxa, normalmente ao ano. "
            "O banco ou o correspondente deve informar o CET antes da contratação. Use o CET, e não só a taxa de juros, para comparar um crédito com outro.")
        + h2("O que é IOF")
        + p("IOF é o Imposto sobre Operações Financeiras. Nesta operação, o parceiro informa que o IOF já está incluído no total que vai para a fatura: "
            "você não paga uma segunda vez. Na Tabela 10, o IOF vai de " + brl(r2["iof"]) + " (2x) a " + brl(r12["iof"]) + " (12x) para cada " + brl(1000) + " recebidos.")
        + h2("Quanto custa, prazo a prazo")
        + tabela(["Parcelas", "Parcela", "Total na fatura", "Custo a mais", "IOF (incluso)", "Juros ao mês", "CET ao ano"], linhas,
                 "Para receber " + brl(1000) + " na conta. Fonte: Tabela 10 do parceiro, conferida toda semana. Página atualizada em " + ctx["atualizado"] + ".")
        + h2("O que a tabela mostra")
        + ul([
            "<strong>O custo total quase não muda com o prazo.</strong> Para receber " + brl(1000) + ", você paga " + brl(extra2) + " a mais em 2x e " + brl(extra12)
            + " a mais em 12x: só " + brl(dif) + " de diferença entre o prazo mais curto e o mais longo.",
            "<strong>A taxa ao mês cai com mais parcelas.</strong> Ela vai de " + pct(r2["jurosMes"]) + " (2x) a " + pct(r12["jurosMes"]) + " (12x). Isso não significa que ficou barato: "
            "o dinheiro fica emprestado por mais tempo, e o total pago é maior.",
            "<strong>O CET ao ano parece enorme em prazos curtos</strong> (" + pct(r2["cetAno"]) + " em 2x) porque uma taxa mensal alta, anualizada, vira um número gigante. "
            "O que pesa de verdade é o valor em reais da coluna &quot;Custo a mais&quot;.",
            "<strong>Mais parcelas só deixam a prestação menor:</strong> em 12x você paga " + brl(r12["parcela"]) + " por mês; em 3x, " + brl(r3["parcela"]) + ".",
        ])
        + aviso("<strong>Regra prática:</strong> antes de contratar, divida o &quot;custo a mais&quot; pelo valor que você recebe. Aqui, para cada R$ 100 recebidos, "
                "você devolve cerca de R$ " + format(round(r12["total"] / 10, 2), ".2f").replace(".", ",") + " em 12x.")
        + h2("Como usar isso")
        + p("Simule com o seu valor na " + a("/#simulador", "calculadora") + ", compare o total com o de outras opções de crédito (veja "
            + a("/emprestimo-com-cartao-ou-outro-credito", "como comparar com outros créditos") + ") e leia " + a("/quando-nao-vale-a-pena", "quando não vale a pena") + ".")
    )


def _ultimas_taxas():
    linhas = tr.ler()
    return [(sr, tr.ultima(sr["codigo"], linhas)) for sr in tr.SERIES], linhas


def _juros_ano(n=12):
    return tr.ano_equivalente(calculo.simular("valor", 1000, 0, n)["jurosMes"])


def _aviso_taxas_medias():
    ultimas, _ = _ultimas_taxas()
    partes = "; ".join(sr["nome"].lower() + ", " + pct(u["taxa_aa"]) + " ao ano" for sr, u in ultimas)
    ref = tr.mes_extenso(max(u["mes"] for _, u in ultimas))
    return ("<strong>Taxas médias do Banco Central (" + ref + "):</strong> " + partes + ". São médias de novas operações de crédito, não ofertas: "
            "a sua taxa pode ser maior ou menor. Veja a " + a("/taxas-de-referencia", "tabela completa, com data e link de cada série") + ".")


def frase_home():
    ultimas, _ = _ultimas_taxas()
    ref = tr.mes_extenso(max(u["mes"] for _, u in ultimas))
    pessoal = next(u for sr, u in ultimas if sr["chave"] == "pessoal-nao-consignado")
    cheque = next(u for sr, u in ultimas if sr["chave"] == "cheque-especial")
    return ("Para comparar: em " + ref + ", a média do Banco Central foi de " + pct(pessoal["taxa_aa"]) + " ao ano no crédito pessoal não consignado e de "
            + pct(cheque["taxa_aa"]) + " no cheque especial. Este empréstimo em 12x tem juros equivalentes a " + pct(_juros_ano(12)) + " ao ano. "
            + a("/taxas-de-referencia", "Veja as taxas de referência") + ".")


def _relacao(valor, ref):
    dif = (valor - ref) / ref
    if abs(dif) < 0.03:
        return "praticamente igual à"
    return "acima da" if valor > ref else "abaixo da"


def corpo_taxas(ctx):
    ultimas, linhas = _ultimas_taxas()
    ref = tr.mes_extenso(max(u["mes"] for _, u in ultimas))
    principal = []
    for sr, u in ultimas:
        principal.append([sr["nome"], tr.mes_extenso(u["mes"]), pct(u["taxa_aa"]), pct(tr.mensal_equivalente(u["taxa_aa"])),
                          pct(tr.media_ultimos(sr["codigo"], 12, linhas)),
                          a(tr.url_json(sr["codigo"]), "série " + str(sr["codigo"]) + " (dados)") + " · " + a(tr.url_catalogo(sr["codigo"]), "catálogo do BCB")])
    base = tr.serie(tr.SERIES[0]["codigo"], linhas)[-13:]
    meses = [r["mes"] for r in base]
    hist = []
    for m in reversed(meses):
        linha = [tr.mes_extenso(m)]
        for sr in tr.SERIES:
            v = next((r["taxa_aa"] for r in tr.serie(sr["codigo"], linhas) if r["mes"] == m), None)
            linha.append(pct(v) if v is not None else "sem dado")
        hist.append(linha)
    nossas = []
    for n in (2, 3, 6, 12):
        r = _r(n)
        nossas.append([str(n) + "x", pct(r["jurosMes"]), pct(tr.ano_equivalente(r["jurosMes"])), pct(r["cetAno"])])
    j12 = _juros_ano(12)
    cmp12 = []
    for sr, u in ultimas:
        cmp12.append(_relacao(j12, u["taxa_aa"]) + " média de " + sr["nome"].lower() + " (" + pct(u["taxa_aa"]) + ")")
    mais_baratas = [sr["nome"].lower() for sr, u in ultimas if u["taxa_aa"] < j12 * 0.97]
    if mais_baratas:
        conclusao = ("Na média do mercado, " + " e ".join(mais_baratas) + " tem juros menores que este empréstimo em 12x. "
                     "Isso não garante que você consiga essa taxa, mas é um motivo para pedir o CET dessas alternativas antes de decidir.")
    else:
        conclusao = "Na média do mercado, nenhuma das três modalidades acima tem juros claramente menores que este empréstimo em 12x."
    return (
        p("Para saber se um crédito é caro, é preciso um ponto de comparação. Esta página reúne as taxas médias de juros divulgadas pelo Banco Central "
          "para três créditos usados por pessoas físicas, com o mês de referência e o link de cada série. São dados de referência: não são oferta de nenhuma instituição.")
        + h2("Taxas médias mais recentes")
        + tabela(["Modalidade", "Mês de referência", "Juros ao ano", "Equivale a, ao mês", "Média dos últimos 12 meses", "Fonte (BCB/SGS)"], principal,
                 "Dados do Banco Central até " + ref + ". Página atualizada em " + ctx["atualizado"] + ".")
        + h2("O que essas taxas são")
        + ul([
            "<strong>Taxa média de juros das novas operações de crédito livre</strong> contratadas no mês, ponderada pelo valor das concessões (conceito do próprio Banco Central).",
            "<strong>Unidade:</strong> percentual ao ano, série mensal. A coluna &quot;ao mês&quot; é a taxa equivalente que calculamos por juros compostos.",
            "<strong>É juros, não é CET.</strong> O CET inclui também IOF e outras despesas, então costuma ser maior que a taxa de juros.",
            "<strong>Tem atraso:</strong> o Banco Central publica cada mês depois de fechado. O mês mais recente aqui é " + ref + ".",
            "<strong>Dados abertos do Banco Central</strong>, licença ODbL. Fonte: Banco Central do Brasil, Sistema Gerenciador de Séries Temporais (SGS).",
        ])
        + h2("Últimos 13 meses")
        + tabela(["Mês"] + [sr["nome"] for sr in tr.SERIES], hist, "Juros ao ano, em %. Mesmas séries da tabela acima.")
        + h2("E o empréstimo com crédito do cartão?")
        + tabela(["Prazo", "Juros ao mês (Tabela 10)", "Equivale a, ao ano", "CET ao ano"], nossas,
                 "Empréstimo com crédito do cartão, Tabela 10 do parceiro. A coluna &quot;ao ano&quot; é a taxa mensal acumulada por 12 meses (juros compostos); como partimos da taxa mensal já arredondada, pode diferir em centésimos do valor que o parceiro mostra.")
        + p("Em 12x, o empréstimo com crédito do cartão tem juros equivalentes a " + pct(j12) + " ao ano: " + "; ".join(cmp12) + ". " + conclusao)
        + p("Em prazos curtos a conta anualizada fica enorme (" + pct(tr.ano_equivalente(_r(2)["jurosMes"])) + " ao ano em 2x) porque a taxa mensal é alta; "
            "o que pesa de verdade é quanto você paga a mais em reais, como mostra " + a("/custo-cet-iof", "CET e IOF") + ".")
        + aviso("<strong>Como ler essa comparação:</strong> as taxas do Banco Central são médias de mercado, e este empréstimo tem taxa tabelada. "
                "Sua taxa em outro crédito depende da sua análise de crédito. Cheque especial e rotativo resolvem situações diferentes, como explica "
                + a("/emprestimo-com-cartao-ou-outro-credito", "a página de comparação") + ". Antes de decidir, peça o CET por escrito.")
        + h2("Como mantemos esta página atualizada")
        + p("Um robô consulta as três séries do SGS toda segunda-feira e grava os últimos 24 meses. Se o Banco Central estiver fora do ar ou mudar o formato da resposta, "
            "o robô não apaga o que já temos e o mês de referência acima mostra até quando os dados vão. Veja a " + a("/metodologia", "Metodologia") + ".")
    )


def corpo_comparar(ctx):
    r12 = _r(12)
    return (
        p("O empréstimo com crédito do cartão, o empréstimo pessoal comum, o cheque especial e o rotativo do cartão resolvem a mesma urgência (falta de dinheiro agora), "
          "mas funcionam de formas diferentes. Esta página dá um método para comparar, sem indicar banco nem produto específico.")
        + h2("As quatro opções, lado a lado")
        + tabela(
            ["", "Empréstimo com crédito do cartão", "Empréstimo pessoal", "Cheque especial", "Rotativo do cartão"],
            [
                ["De onde vem o dinheiro", "Do limite do cartão de crédito", "Da instituição, sem usar o limite do cartão", "Do limite da conta corrente", "Não vem dinheiro: é uma dívida da fatura"],
                ["Como o dinheiro chega", "Pix, em chave em seu nome", "Em geral, crédito na conta", "Usa o limite da conta corrente", "Não chega dinheiro: é uma dívida da fatura"],
                ["Como você paga", "Parcelas na fatura do cartão", "Parcelas fixas, em geral debitadas ou em boleto", "Quitar o saldo usado, com juros por dia", "Pagando o restante da fatura, com juros"],
                ["Prazo", "2 a 12 parcelas", "Definido no contrato", "Sem prazo fixo: dura enquanto o saldo estiver negativo", "Sem prazo fixo: dura enquanto a fatura não for quitada"],
                ["Onde o custo aparece", "CET na tela de contratação", "CET no contrato", "Juros cobrados sobre o saldo usado", "Juros sobre o saldo da fatura não pago"],
            ],
            "Descrição geral. Condições variam por instituição; confira sempre no contrato.")
        + h2("Como comparar de forma justa")
        + ol([
            "<strong>Compare o mesmo valor.</strong> Peça a simulação do mesmo valor que você precisa nas duas ou três opções.",
            "<strong>Compare o total pago, não só a parcela.</strong> Uma parcela baixa em prazo longo pode custar mais no total.",
            "<strong>Compare o CET.</strong> Ele inclui juros, IOF e outras despesas. Duas taxas de juros iguais podem ter CETs diferentes.",
            "<strong>Veja o que acontece se você atrasar.</strong> Multa, juros de mora e o efeito sobre a fatura do cartão.",
            "<strong>Veja quanto tempo você precisa do dinheiro.</strong> Para poucos dias, cheque especial e rotativo têm lógica diferente de um crédito com prazo.",
        ])
        + h2("O que é específico do empréstimo com crédito do cartão")
        + ul([
            "O custo é conhecido antes: você vê o total e o CET. Para " + brl(1000) + " em 12x, o total é " + brl(r12["total"]) + ".",
            "As parcelas entram na fatura e disputam espaço com as suas compras do mês, e o total fica comprometido no limite do cartão. Se a fatura não for paga por inteiro, o saldo pode ficar sujeito aos juros do cartão.",
            "O valor é limitado a R$ 5.000 e depende de análise de crédito.",
        ])
        + aviso(_aviso_taxas_medias())
        + p("Veja também " + a("/custo-cet-iof", "CET e IOF: quanto custa de verdade") + " e " + a("/quando-nao-vale-a-pena", "quando não vale a pena") + ".")
    )


def corpo_quando_nao(ctx):
    r500_3 = _r(3, 500)
    r1000_12 = _r(12)
    return (
        p("Crédito caro serve para poucas situações. Esta página lista as ocasiões em que o empréstimo com crédito do cartão costuma ser má ideia, e as poucas em que pode fazer sentido. "
          "Não é recomendação financeira: é um roteiro de perguntas para você responder antes de clicar.")
        + h2("Quando NÃO vale a pena")
        + ul([
            "<strong>Quando existe crédito mais barato ao seu alcance.</strong> Compare o total e o CET (veja " + a("/emprestimo-com-cartao-ou-outro-credito", "como comparar") + ").",
            "<strong>Quando você não tem certeza de que vai pagar a fatura inteira.</strong> As parcelas somam com as compras do mês. Fatura não paga por inteiro pode gerar juros do cartão por cima.",
            "<strong>Quando a necessidade é de longo prazo.</strong> Para receber " + brl(1000) + " em 12x, você paga " + brl(r1000_12["total"]) + ". Se o problema é recorrente, o crédito só adia e aumenta o buraco.",
            "<strong>Para quitar uma dívida que já tem juros menores.</strong> Trocar uma dívida mais barata por esta piora a situação.",
            "<strong>Para apostar, investir ou comprar criptomoeda.</strong> Usar crédito caro para isso é receita de prejuízo.",
            "<strong>Quando alguém pede pagamento adiantado ou chave Pix de terceiro.</strong> É golpe (veja " + a("/e-seguro-golpes", "como evitar golpes") + ").",
            "<strong>Quando você ainda não leu o total e o CET na tela final.</strong> Se algo não bate com a simulação, pare.",
        ])
        + h2("Quando pode fazer sentido")
        + ul([
            "Uma emergência de curto prazo, sem alternativa mais barata, com valor que você sabe pagar na fatura.",
            "Um valor pequeno, em prazo curto, em que o &quot;custo a mais&quot; em reais cabe no seu orçamento. Exemplo: receber " + brl(500) + " em 3x significa pagar "
            + brl(r500_3["total"]) + " na fatura, ou seja, " + brl(r500_3["total"] - 500) + " a mais.",
        ])
        + h2("Perguntas para você responder")
        + ol([
            "Quanto eu pago a mais, em reais, e isso cabe no meu orçamento?",
            "Eu já pedi o CET de uma alternativa?",
            "Se eu receber menos do que esperava este mês, ainda consigo pagar a fatura inteira?",
            "Eu preciso desse dinheiro ou quero comprar algo que posso adiar?",
        ])
        + aviso("Se a resposta à primeira pergunta é &quot;não sei&quot;, volte à " + a("/#simulador", "calculadora") + " e olhe o total na fatura antes de decidir.")
    )


def corpo_metodologia(ctx):
    r12 = _r(12)
    return (
        p("Todos os números do simulador vêm da Tabela 10 do parceiro. Esta página mostra a conta, de onde vêm os dados e como conferimos que continuam certos.")
        + h2("A conta")
        + ul([
            "<strong>Fator</strong> = 0,5479 + 0,003 x número de parcelas.",
            "<strong>Total na fatura</strong> = valor recebido x (1 + fator).",
            "<strong>Parcela</strong> = total na fatura / número de parcelas.",
            "<strong>IOF</strong> = valor recebido x (0,0038 + 0,00246 x número de parcelas). Já está dentro do total.",
            "<strong>Juros ao mês e CET ao ano</strong>: tabelados pelo parceiro, de " + pct(_r(2)["jurosMes"]) + " ao mês e " + pct(_r(2)["cetAno"]) + " ao ano em 2x até "
            + pct(r12["jurosMes"]) + " ao mês e " + pct(r12["cetAno"]) + " ao ano em 12x.",
            "<strong>Modo &quot;usar meu limite&quot;:</strong> valor recebido = limite / (1 + fator), com teto de R$ 5.000.",
            "<strong>Taxa de uma proposta que você já tem:</strong> é a taxa mensal que faz as parcelas iguais valerem, hoje, o valor que você recebe (juros compostos, sem tarifas). A comparação põe a proposta e a Tabela 10 na mesma conta; por isso o número da Tabela 10 aparece um pouco acima do que o parceiro tabela (ele usa outro método). Serve só para comparar.",
        ])
        + p("Exemplo conferido: " + brl(1000) + " em 12x dá parcela de " + brl(r12["parcela"]) + ", total de " + brl(r12["total"]) + " e IOF de " + brl(r12["iof"]) + ".")
        + h2("De onde vêm os dados")
        + p("Da Tabela 10 do parceiro (correspondente bancário). Os limites vigentes são de R$ 300 a R$ 5.000 e de 2 a 12 parcelas. Não usamos taxa estimada nem média de mercado nesta conta.")
        + h2("Como conferimos")
        + ul([
            "Toda segunda-feira, um robô pergunta à API do próprio parceiro o resultado de " + brl(1000) + " em cada prazo (2x a 12x) e compara parcela, total, IOF, juros e CET com a nossa conta.",
            "Também confere o valor máximo, o número máximo de parcelas e o nome da tabela. Se algo mudar, a verificação falha e o dono do projeto é avisado.",
            "Testes automáticos garantem que a conta no navegador (JavaScript) dá o mesmo resultado que a conta em Python.",
            "O código é aberto: " + a(GITHUB, "repositório no GitHub") + ".",
        ])
        + h2("O que esta conta não cobre")
        + ul([
            "A aprovação do crédito, que é decisão do parceiro, e o valor final que ele oferecer para você.",
            "Mudanças feitas pelo parceiro entre uma conferência e outra. A data de atualização está no rodapé de cada página.",
            "Como o emissor do seu cartão libera o limite conforme você paga as parcelas: é regra dele.",
            "Condições de outros créditos: este site não compara bancos nem instituições.",
        ])
        + h2("Taxas de referência do Banco Central")
        + p("As taxas de outros créditos vêm das séries 20742 (crédito pessoal não consignado), 20741 (cheque especial) e 22022 (cartão de crédito rotativo) do SGS, "
            "todas de pessoas físicas, mensais e em percentual ao ano. Os códigos foram conferidos no catálogo de dados abertos do Banco Central. "
            "Um robô as atualiza toda segunda-feira. Detalhes e números em " + a("/taxas-de-referencia", "Taxas de referência") + ". Os dados estão em " + a("/dados-abertos", "Dados abertos") + ".")
        + h2("Medição de uso")
        + p("Usamos o Umami, que não usa cookies. Ele registra visitas e alguns eventos (quando você mexe na simulação, abre a tela de confirmação, continua para o parceiro ou copia o link), "
            "com valor e prazo. Não registramos CPF, telefone nem dados pessoais. Detalhes em " + a("/privacidade", "Privacidade") + ".")
    )


def corpo_sobre(ctx):
    return (
        p("Datalab Global é uma marca de " + ctx["razao"] + ", CNPJ " + ctx["cnpj"] + ". Este simulador existe para mostrar o custo real do empréstimo pessoal com crédito do cartão antes de você decidir.")
        + h2("Quem realiza a operação")
        + p("A operação é de um parceiro, correspondente bancário. O ambiente de contratação é dele, e a análise e a aprovação de crédito também. "
            "A Datalab Global não concede crédito e não é banco.")
        + p("O botão \"Continuar para o parceiro\" só aparece depois da tela de confirmação, com o total em reais. Ele leva ao ambiente do parceiro, em outro site, "
            "onde ficam os passos da contratação, inclusive o pedido de CPF e de documento original. Antes de concluir, confira lá o valor, as parcelas e o CET.")
        + h2("Por que este simulador existe")
        + p("Esse tipo de empréstimo costuma ser anunciado pela facilidade: o dinheiro cai rápido e a parcela cabe na fatura. O que quase nunca aparece é o total. "
            "Montamos este simulador para inverter a ordem: primeiro o custo em reais e o CET, depois o botão. Quando uma alternativa mais barata existe, "
            "dizemos isso nos guias, mesmo que a pessoa deixe de contratar.")
        + h2("O que fazemos e o que não fazemos")
        + ul([
            "Mostramos parcela, total, IOF e CET com a conta do parceiro, conferida toda semana (veja " + a("/metodologia", "Metodologia") + ").",
            "Não coletamos dado pessoal neste site. O CPF e o documento são pedidos só no ambiente do parceiro.",
            "Não vendemos anúncio nem usamos cookies de publicidade.",
            "Não fazemos ranking de bancos nem indicamos instituição específica.",
            "Não garantimos aprovação: ela depende da análise de crédito do parceiro.",
        ])
        + h2("Contato")
        + p("E-mail: " + a("mailto:" + ctx["email"], ctx["email"]) + ". Se você encontrar um número errado ou uma informação desatualizada, escreva: corrigimos e registramos em "
            + a("/atualizacoes", "Atualizações") + ".")
    )


def corpo_atualizacoes(ctx):
    itens = "".join("<li><b>" + d + "</b> — " + t + "</li>" for d, t in ctx["atualizacoes"])
    return (
        p("Registro das mudanças relevantes: conferências da tabela do parceiro, correções e novas páginas. A mais recente aparece primeiro.")
        + '<ul class="hist">' + itens + "</ul>\n"
    )


ATUALIZACOES = [
    ("20/11/2026", "Correção do nome: o produto passou a se chamar Empréstimo pessoal com crédito do cartão, porque é um empréstimo pessoal em que o limite do cartão é a fonte do dinheiro, entregue por Pix. O nome antigo induzia a erro. A página de comparação mudou de endereço (o antigo continua funcionando e leva ao novo) e os arquivos de dados abertos também (os endereços antigos redirecionam). Os eventos de medição foram renomeados. A conta e os números não mudaram."),
    ("20/11/2026", "Novo visual do simulador, igual ao dos outros simuladores da Datalab Global: cartões por campo, painel de resultado, faixa com três números, campo para comparar a taxa de uma proposta que você já tem, tela de confirmação antes de abrir o parceiro, logo redesenhado e rodapé com os demais simuladores."),
    ("17/11/2026", "Os dois conjuntos de dados abertos também estão no Hugging Face, com a mesma licença (link na página Dados abertos)."),
    ("16/11/2026", "Revisão geral do site, com correções: a home chamava os juros ao mês de CET (agora diz juros ao mês e CET ao ano); o modo usar meu limite passou a aceitar limites a partir de R$ 300 e mostra quanto falta para o mínimo; se não conseguirmos pré-preencher a proposta no parceiro, avisamos antes de abrir a tela dele; no celular, uma barra fixa mostra parcela e total enquanto você mexe nos controles; o campo de valor aceita milhar e vírgula; o menu fecha ao tocar fora; títulos mais curtos e acessibilidade das abas e dos controles deslizantes."),
    ("15/11/2026", "Visual em roxo, com logo e ícones novos, e botões e links do celular com 44 px de altura."),
    ("14/11/2026", "Novo visual, na mesma família dos outros simuladores da Datalab Global: títulos em Playfair Display, texto em Inter (fontes servidas pelo próprio site), gráfico da composição do total e barras com o custo a mais por prazo. A conta e os números não mudaram."),
    ("14/11/2026", "Simulador no ar em emprestimo.datalabglobal.com. Os dois conjuntos de dados abertos também estão no Kaggle, com a mesma licença."),
    ("14/11/2026", "Correção: removemos a citação da Resolução CMN nº 3.954/2011, que foi revogada (o texto consolidado do Banco Central aponta a Resolução BCB nº 277/2022). Os textos agora falam em normas do Banco Central e do CMN sobre correspondentes."),
    ("14/11/2026", "Dados abertos (Tabela 10 em CC BY 4.0 e séries do Banco Central em ODbL 1.0), feed Atom e aviso ao Bing por IndexNow."),
    ("14/11/2026", "Taxas médias do Banco Central (crédito pessoal não consignado, cheque especial e cartão rotativo) com mês de referência e link de cada série, e comparação com este empréstimo."),
    ("14/11/2026", "Guias com conteúdo próprio (como funciona, golpes, CET e IOF, comparação, quando não vale a pena), metodologia, página Sobre, privacidade e termos."),
    ("13/11/2026", "Conta do simulador conferida com a API do parceiro: R$ 1.000 em 2x a 12x, mesma Tabela 10, limites de R$ 300 a R$ 5.000 e 12 parcelas. Nenhuma diferença."),
    ("13/11/2026", "Simulador extraído do hub da Datalab Global para este projeto independente, com medição de uso sem cookies."),
]


def _secoes(secoes):
    return "".join(h2(t) + "".join(p(x) for x in ps) for t, ps in secoes)


def corpo_dados_abertos(ctx):
    saida = (
        p("Os números deste simulador estão disponíveis para baixar, em CSV e JSON, para quem quiser conferir, citar ou usar em outra análise. "
          "São dois conjuntos, e cada um segue a licença que a sua fonte permite.")
    )
    for c in da.CONJUNTOS:
        lic = c["licenca"]
        arquivos = [
            [a("/dados/" + c["nome"] + ".csv", c["nome"] + ".csv"), "CSV, UTF-8"],
            [a("/dados/" + c["nome"] + ".json", c["nome"] + ".json"), "JSON"],
            [a("/dados/datapackage-" + c["nome"] + ".json", "datapackage-" + c["nome"] + ".json"), "Descrição do conjunto (Data Package)"],
            [a(c["kaggle"], "Kaggle"), "Cópia no Kaggle (mesma licença)"],
            [a(c["huggingface"], "Hugging Face"), "Cópia no Hugging Face (mesma licença)"],
        ]
        saida += (
            h2(c["titulo"])
            + p(c["descricao"])
            + tabela(["Arquivo", "Formato"], arquivos, "Atualizado toda semana. Página atualizada em " + ctx["atualizado"] + ".")
            + h3("Licença: " + lic["titulo"])
            + p(da.texto_licenca(c).replace(lic["url"], a(lic["url"], lic["url"])))
            + h3("Colunas")
            + ul(["<code>" + n + "</code>: " + d for n, _t, d in c["colunas"]])
        )
    saida += (
        h2("Como citar")
        + p("Cite como: " + da.CITACAO + ", com a data de acesso. Para o conjunto do Banco Central, cite também o Banco Central do Brasil como fonte original.")
        + h2("Por que a licença do conjunto do Banco Central é diferente")
        + p("O Banco Central publica essas séries sob a licença ODbL, que exige que bases derivadas mantenham a mesma licença. Por isso esse conjunto não é CC BY. "
            "A tabela do empréstimo com crédito do cartão é nossa compilação das condições do parceiro e segue a CC BY 4.0.")
        + h2("Limites")
        + ul([
            "As taxas do Banco Central são médias de mercado das operações novas, não ofertas. A taxa que você receber pode ser maior ou menor.",
            "A Tabela 10 é do parceiro e pode mudar; a conferência com a API dele é semanal (veja " + a("/metodologia", "Metodologia") + ").",
            "Os endereços antigos dos arquivos (com o nome anterior do produto) redirecionam para os novos. Os cadastros no Kaggle e no Hugging Face foram criados com o nome antigo e podem demorar a mostrar o novo título.",
            "Para acompanhar as atualizações, use o " + a("/feed.xml", "feed Atom") + " ou a página " + a("/atualizacoes", "Atualizações") + ".",
        ])
    )
    return saida


def corpo_privacidade(ctx):
    return (
        p("Esta Política explica como este site trata dados pessoais, em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018). Última atualização: "
          + ctx["atualizado"] + ".")
        + _secoes([
            ("1. Dados que este site coleta",
             ["Nenhum dado pessoal é pedido neste site. Você informa apenas valor e prazo, que ficam no seu navegador. "
              "Se você escrever para " + ctx["email"] + ", guardamos o seu e-mail e o conteúdo da mensagem para responder."]),
            ("2. Medição de uso",
             ["Usamos o Umami, que não usa cookies e não identifica você. Ele conta visitas e eventos (quando você usa a simulação, abre a tela de confirmação, continua para o parceiro ou copia o link), com valor e prazo. "
              "A hospedagem (Cloudflare) pode tratar o endereço IP para entregar o site e proteger contra ataques."]),
            ("3. Ao pedir a proposta",
             ["Ao continuar para o parceiro, este site envia a ele só o valor e o prazo simulados e abre o ambiente de contratação dele. "
              "A partir daí, os dados que você digitar (CPF, documento, dados do cartão) são tratados pelo parceiro, conforme a política dele, e não passam por este site."]),
            ("4. Bases legais",
             ["Tratamos dados com base no legítimo interesse (segurança e melhoria do site), no cumprimento de obrigações legais e, quando for o caso, no seu consentimento."]),
            ("5. Compartilhamento",
             ["Não vendemos dados. Compartilhamos o mínimo com provedores que operam o site (hospedagem e medição), sob contrato."]),
            ("6. Seus direitos",
             ["Você pode pedir confirmação de tratamento, acesso, correção, eliminação e revogação de consentimento, a qualquer momento, pelo e-mail " + ctx["email"] + "."]),
            ("7. Cookies",
             ["Este site não usa cookies de publicidade nem de rastreamento."]),
            ("8. Contato e alterações",
             ["O canal para assuntos de privacidade é " + ctx["email"] + ". Esta Política pode ser atualizada; vale a versão publicada nesta página. Responsável: "
              + ctx["razao"] + ", CNPJ " + ctx["cnpj"] + "."]),
        ])
    )


def corpo_termos(ctx):
    return (
        p("Estes Termos regulam o uso deste site. Ao usar o site, você concorda com as condições abaixo. Última atualização: " + ctx["atualizado"] + ".")
        + _secoes([
            ("1. O que é este site",
             ["Um simulador do empréstimo pessoal com crédito do cartão, mantido por " + ctx["razao"] + " (marca Datalab Global). Ele mostra estimativas e leva você ao ambiente de um parceiro, que é quem faz a operação."]),
            ("2. A simulação não é proposta de crédito",
             ["Os números seguem a Tabela 10 do parceiro, conferida toda semana, mas são informativos. Não são oferta, promessa de crédito nem recomendação financeira. "
              "A aprovação, o valor e as condições finais dependem da análise de crédito do parceiro."]),
            ("3. Uso permitido",
             ["Você pode usar o site para fins lícitos. É proibido tentar acessar áreas restritas, sobrecarregar a infraestrutura ou extrair dados em massa de forma automatizada sem autorização."]),
            ("4. Propriedade intelectual",
             ["Marca, layout e textos pertencem aos seus titulares. Os dados abertos, quando publicados, terão a licença indicada na própria página."]),
            ("5. Limitação de responsabilidade",
             ["O site é oferecido no estado em que se encontra. Fazemos esforços razoáveis para mantê-lo correto e disponível, mas não garantimos ausência de falhas. A relação de crédito é entre você e o parceiro."]),
            ("6. Alterações e contato",
             ["Podemos atualizar estes Termos; vale a versão publicada nesta página. Dúvidas: " + ctx["email"] + "."]),
        ])
    )


# Slug que mudou (precisa de redirecionamento 301 no _redirects, feito pelo gerador): o antigo continha o nome errado do produto.
SLUG_COMPARAR = "emprestimo-com-cartao-ou-outro-credito"
REDIRECIONAMENTOS_SLUG = {"/pix-no-cartao-ou-outro-credito": "/" + SLUG_COMPARAR}

# slug, título (title, até 60 caracteres), h1, descrição, corpo, rótulo no menu
PAGINAS = [
    dict(slug="como-funciona", menu="Como funciona", title="Como funciona o empréstimo pessoal com crédito do cartão",
         h1="Como funciona o empréstimo pessoal com crédito do cartão",
         desc="O limite do cartão é a fonte do dinheiro: o valor cai por Pix e você paga na fatura. Veja o passo a passo, a CCB, o limite e o que ter em mãos.",
         corpo=corpo_como_funciona),
    dict(slug="e-seguro-golpes", menu="É seguro?", title="Empréstimo com crédito do cartão é seguro? Evite golpes",
         h1="Empréstimo pessoal com crédito do cartão é seguro? Como evitar golpes",
         desc="O que dá para verificar (CNPJ, CCB, correspondente bancário), os sinais de golpe de crédito e o que fazer se cair em um.",
         corpo=corpo_seguro),
    dict(slug="custo-cet-iof", menu="CET e IOF", title="CET e IOF do empréstimo com crédito do cartão: o custo real",
         h1="CET e IOF do empréstimo com crédito do cartão: quanto custa de verdade",
         desc="Tabela com parcela, total, IOF, juros e CET de 2x a 12x para R$ 1.000. Veja por que o prazo muda a parcela, mas quase não muda o custo.",
         corpo=corpo_custo),
    dict(slug=SLUG_COMPARAR, menu="Comparar créditos",
         title="Empréstimo com cartão ou outro crédito: como comparar",
         h1="Empréstimo com crédito do cartão, pessoal, cheque especial ou rotativo: como comparar",
         desc="Método para comparar quatro tipos de crédito pelo total pago e pelo CET, sem indicar banco: o que muda em origem do dinheiro, prazo, pagamento e custo.",
         corpo=corpo_comparar),
    dict(slug="taxas-de-referencia", menu="Taxas do BC", title="Taxas do Banco Central: cheque especial, pessoal e rotativo",
         h1="Taxas médias do Banco Central: cheque especial, crédito pessoal e rotativo",
         desc="Taxas médias de juros de três créditos para pessoa física, com mês de referência e link de cada série, comparadas ao empréstimo com crédito do cartão.",
         corpo=corpo_taxas),
    dict(slug="quando-nao-vale-a-pena", menu="Quando não vale", title="Quando o empréstimo com crédito do cartão não vale a pena",
         h1="Quando o empréstimo com crédito do cartão não vale a pena (e quando pode valer)",
         desc="Sete situações em que este crédito caro costuma ser má ideia, as poucas em que pode fazer sentido e perguntas para decidir.",
         corpo=corpo_quando_nao),
    dict(slug="metodologia", menu="Metodologia", title="Metodologia: como calculamos o empréstimo com cartão",
         h1="Metodologia: como calculamos o empréstimo pessoal com crédito do cartão",
         desc="A conta (fator, parcela, IOF, CET), a fonte (Tabela 10 do parceiro), a conferência semanal pela API e o que o simulador não cobre.",
         corpo=corpo_metodologia),
    dict(slug="sobre", menu="Sobre", title="Sobre a Datalab Global e este simulador",
         h1="Sobre a Datalab Global e este simulador",
         desc="Quem mantém o simulador, quem realiza a operação (correspondente bancário), o que fazemos e o que não fazemos, e como falar com a gente.",
         corpo=corpo_sobre),
    dict(slug="dados-abertos", menu=None, title="Dados abertos: empréstimo com cartão e taxas do BC",
         h1="Dados abertos: empréstimo com crédito do cartão e taxas do Banco Central",
         desc="Baixe em CSV e JSON a Tabela 10 do empréstimo com crédito do cartão (CC BY 4.0) e as taxas médias do Banco Central (ODbL 1.0), com colunas, licença e como citar.",
         corpo=corpo_dados_abertos),
    dict(slug="atualizacoes", menu=None, title="Atualizações do simulador de empréstimo com cartão",
         h1="Atualizações do simulador de empréstimo pessoal com crédito do cartão",
         desc="Registro de conferências da tabela do parceiro, correções, melhorias de uso e novas páginas do simulador do empréstimo pessoal com crédito do cartão.",
         corpo=corpo_atualizacoes, min_palavras=60),
    dict(slug="privacidade", menu=None, title="Política de Privacidade", h1="Política de Privacidade",
         desc="Como este site trata dados: nenhum dado pessoal pedido, medição sem cookies e o que o parceiro faz com seus dados na contratação.",
         corpo=corpo_privacidade, guia=False),
    dict(slug="termos", menu=None, title="Termos de Uso", h1="Termos de Uso",
         desc="Regras de uso do simulador do empréstimo com crédito do cartão: a simulação não é proposta de crédito, uso permitido e limites de responsabilidade.",
         corpo=corpo_termos, guia=False),
]
