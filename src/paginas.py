"""Montagem das páginas HTML da versão web do CarManager.

Regra de segurança: todo texto digitado pelo usuário passa por e()
(escape) antes de entrar no HTML.
"""

from datetime import date
from html import escape

from abastecimentos import (
    COMBUSTIVEIS_ABASTECIMENTO,
    abastecimentos_do_veiculo,
    calcular_consumo_medio,
)
from gastos import CATEGORIAS, gastos_do_veiculo, total_gastos
from manutencoes import TIPOS_MANUTENCAO, manutencoes_do_veiculo, ultima_manutencao
from utils import formatar_data, formatar_km, formatar_moeda, formatar_numero
from veiculos import COMBUSTIVEIS, descricao_veiculo


def e(valor):
    """Escapa um texto para uso seguro dentro do HTML."""
    return escape(str(valor), quote=True)


# ---------------------------------------------------------------- Peças reutilizáveis

def layout(titulo, conteudo, ativo="", mensagem=""):
    """Moldura comum a todas as páginas: menu lateral e área principal."""
    itens = [("inicio", "/", "Visão geral"),
             ("veiculos", "/veiculos", "Veículos"),
             ("novo", "/veiculos/novo", "Novo veículo")]
    links = ""
    for chave, destino, texto in itens:
        classe = ' class="ativo"' if chave == ativo else ""
        icones = {
            "inicio": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
            "veiculos": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 11l1.5-4A2 2 0 0 1 8.4 5.5h7.2a2 2 0 0 1 1.9 1.5l1.5 4"/><path d="M3.5 11.5A2.5 2.5 0 0 1 6 9h12a2.5 2.5 0 0 1 2.5 2.5V17H3.5z"/><path d="M6 17v2m12-2v2M6 13h2m8 0h2"/></svg>',
            "novo": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></svg>',
        }
        icone = icones[chave]
        links += (f'<a href="{destino}"{classe}><span class="nav-icone">{icone}</span>'
                  f'<span>{texto}</span></a>')

    aviso = ""
    if mensagem:
        aviso = f'<div class="aviso sucesso">{e(mensagem)}</div>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#17145f">
<title>{e(titulo)} - CarManager</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<aside class="sidebar" id="sidebar">
  <a class="logo" href="/"><span class="logo-simbolo">C</span><span>CarManager<small>GESTÃO DE VEÍCULOS</small></span></a>
  <div class="menu-titulo">MENU PRINCIPAL</div>
  <nav class="menu-lateral">{links}</nav>
  <div class="sidebar-rodape"><span class="avatar">CM</span><div><strong>CarManager</strong><small>Seu controle automotivo</small></div></div>
</aside>
<div class="conteudo-app">
  <header class="topbar">
    <button class="menu-toggle" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="sidebar"><span></span><span></span><span></span></button>
    <div><span class="topbar-eyebrow">SEU PAINEL, SEU CONTROLE</span><strong>Gestão inteligente do seu veículo</strong></div>
    <a class="botao topbar-botao" href="/veiculos/novo">+ Novo veículo</a>
  </header>
  <main class="container">
    {aviso}
    {conteudo}
  </main>
  <footer class="rodape container">CarManager · Projeto escolar ETEC · Dados fictícios</footer>
</div>
<script src="/static/app.js" defer></script>
</body>
</html>"""


def lista_erros(erros):
    if not erros:
        return ""
    itens = "".join(f"<li>{e(erro)}</li>" for erro in erros)
    return ('<div class="aviso erro"><strong>Corrija os campos abaixo:</strong>'
            f"<ul>{itens}</ul></div>")


def campo(nome, rotulo, valor="", tipo="text", extra=""):
    return (f'<label>{e(rotulo)}'
            f'<input type="{tipo}" name="{nome}" value="{e(valor)}" {extra}></label>')


def seletor(nome, rotulo, opcoes, valor=""):
    itens = ""
    for opcao in opcoes:
        marcado = " selected" if opcao == valor else ""
        itens += f'<option value="{e(opcao)}"{marcado}>{e(opcao)}</option>'
    return f'<label>{e(rotulo)}<select name="{nome}">{itens}</select></label>'


def tabela(cabecalhos, linhas):
    """Cabeçalhos e células já devem vir como HTML seguro."""
    cab = "".join(f"<th>{c}</th>" for c in cabecalhos)
    corpo = ""
    for linha in linhas:
        corpo += "<tr>" + "".join(f"<td>{c}</td>" for c in linha) + "</tr>"
    return (f'<div class="tabela-rolavel"><table><thead><tr>{cab}</tr></thead>'
            f"<tbody>{corpo}</tbody></table></div>")


def cartao(rotulo, valor, classe=""):
    return (f'<div class="cartao {classe}"><span class="rotulo">{e(rotulo)}</span>'
            f"<strong>{valor}</strong></div>")


def cabecalho_veiculo(veiculo, ativo):
    """Título do veículo + abas (Resumo, Abastecimentos, ...)."""
    base = f"/veiculos/{veiculo['id']}"
    abas = [("resumo", base, "Resumo"),
            ("abastecimentos", base + "/abastecimentos", "Abastecimentos"),
            ("manutencoes", base + "/manutencoes", "Manutenções"),
            ("gastos", base + "/gastos", "Gastos"),
            ("editar", base + "/editar", "Editar")]
    links = ""
    for chave, destino, texto in abas:
        classe = ' class="ativo"' if chave == ativo else ""
        links += f'<a href="{destino}"{classe}>{texto}</a>'
    return (f"<h1>{e(veiculo['marca'])} {e(veiculo['modelo'])}</h1>"
            f'<p class="subtitulo">{e(veiculo["ano"])} &middot; {e(veiculo["cor"])} '
            f'&middot; Placa {e(veiculo["placa"])}</p>'
            f'<nav class="abas">{links}</nav>')


def tabela_veiculos(veiculos):
    linhas = []
    for v in veiculos:
        linhas.append([
            v["id"], e(v["marca"]), e(v["modelo"]), v["ano"], e(v["cor"]),
            formatar_km(v["km"]), e(v["combustivel"]), e(v["placa"]),
            f'<a class="botao pequeno" href="/veiculos/{v["id"]}">Abrir</a>',
        ])
    return tabela(["ID", "Marca", "Modelo", "Ano", "Cor", "Km", "Combustível",
                   "Placa", ""], linhas)


# ---------------------------------------------------------------- Páginas gerais

def pagina_erro(titulo, mensagem):
    conteudo = (f"<h1>{e(titulo)}</h1><p>{e(mensagem)}</p>"
                '<p><a class="botao" href="/">Voltar ao início</a></p>')
    return layout(titulo, conteudo)


def pagina_inicio(dados, mensagem=""):
    total_geral = sum(g["valor"] for g in dados["gastos"])
    cartoes = (cartao("Veículos", len(dados["veiculos"]))
               + cartao("Abastecimentos", len(dados["abastecimentos"]))
               + cartao("Manutenções", len(dados["manutencoes"]))
               + cartao("Total gasto", formatar_moeda(total_geral), "destaque"))

    if dados["veiculos"]:
        lista = tabela_veiculos(dados["veiculos"])
    else:
        lista = ('<div class="vazio"><p>Nenhum veículo cadastrado ainda.</p>'
                 '<a class="botao" href="/veiculos/novo">Cadastrar primeiro veículo</a></div>')

    conteudo = ('<h1>Painel</h1><p class="subtitulo">Visão geral dos seus veículos.</p>'
                f'<div class="cartoes">{cartoes}</div><h2>Seus veículos</h2>{lista}')
    return layout("Início", conteudo, "inicio", mensagem)


def pagina_veiculos(dados, mensagem=""):
    if dados["veiculos"]:
        lista = tabela_veiculos(dados["veiculos"])
    else:
        lista = ('<div class="vazio"><p>Nenhum veículo cadastrado.</p>'
                 '<a class="botao" href="/veiculos/novo">Cadastrar veículo</a></div>')
    conteudo = ('<div class="linha-titulo"><div><h1>Veículos</h1>'
                f'<p class="subtitulo">{len(dados["veiculos"])} veículo(s) cadastrado(s).</p></div>'
                '<a class="botao" href="/veiculos/novo">+ Novo veículo</a></div>'
                f"{lista}")
    return layout("Veículos", conteudo, "veiculos", mensagem)


# ---------------------------------------------------------------- Veículo

def pagina_form_veiculo(valores, erros, veiculo_id=None):
    editando = veiculo_id is not None
    titulo = "Editar veículo" if editando else "Cadastrar veículo"
    acao = f"/veiculos/{veiculo_id}/editar" if editando else "/veiculos/novo"
    cancelar = f"/veiculos/{veiculo_id}" if editando else "/veiculos"
    ano_max = date.today().year + 1

    campos = (
        campo("marca", "Marca", valores.get("marca", ""), extra="required")
        + campo("modelo", "Modelo", valores.get("modelo", ""), extra="required")
        + campo("ano", "Ano", valores.get("ano", ""), "number",
                f'min="1900" max="{ano_max}" required')
        + campo("cor", "Cor", valores.get("cor", ""), extra="required")
        + campo("km", "Quilometragem atual (km)", valores.get("km", ""), "number",
                'min="0" required')
        + seletor("combustivel", "Tipo de combustível", COMBUSTIVEIS,
                  valores.get("combustivel", ""))
        + campo("placa", "Placa fictícia (ABC-1234 ou ABC1D23)",
                valores.get("placa", ""), extra='maxlength="8" required')
    )
    conteudo = (
        f"<h1>{titulo}</h1>"
        '<p class="subtitulo">Use apenas dados fictícios.</p>'
        f"{lista_erros(erros)}"
        f'<form class="painel formulario" method="post" action="{acao}">'
        f'<div class="grade">{campos}</div>'
        '<div class="acoes"><button class="botao" type="submit">Salvar</button>'
        f'<a class="botao secundario" href="{cancelar}">Cancelar</a></div></form>'
    )
    return layout(titulo, conteudo, "" if editando else "novo")


def pagina_veiculo(dados, veiculo, mensagem=""):
    vid = veiculo["id"]
    abastecimentos = abastecimentos_do_veiculo(dados, vid)
    manutencoes = manutencoes_do_veiculo(dados, vid)
    ultima = ultima_manutencao(manutencoes)
    consumo = calcular_consumo_medio(abastecimentos)

    cartoes_gastos = (
        cartao("Quilometragem atual", formatar_km(veiculo["km"]))
        + cartao("Total gasto", formatar_moeda(total_gastos(dados, vid)), "destaque")
        + cartao("Gasto com combustível",
                 formatar_moeda(total_gastos(dados, vid, "Combustível")))
        + cartao("Gasto com manutenção",
                 formatar_moeda(total_gastos(dados, vid, "Manutenção")))
    )
    texto_consumo = "dados insuficientes" if consumo is None else f"{formatar_numero(consumo)} km/l"
    cartoes_registros = (
        cartao("Abastecimentos", len(abastecimentos))
        + cartao("Manutenções", len(manutencoes))
        + cartao("Consumo médio", texto_consumo)
    )

    if ultima is None:
        bloco_ultima = "<p>Nenhuma manutenção registrada.</p>"
    else:
        bloco_ultima = (
            "<dl>"
            f"<div><dt>Data</dt><dd>{formatar_data(ultima['data'])}</dd></div>"
            f"<div><dt>Tipo</dt><dd>{e(ultima['tipo'])}</dd></div>"
            f"<div><dt>Quilometragem</dt><dd>{formatar_km(ultima['km'])}</dd></div>"
            f"<div><dt>Descrição</dt><dd>{e(ultima['descricao'] or '-')}</dd></div>"
            f"<div><dt>Valor</dt><dd>{formatar_moeda(ultima['valor'])}</dd></div>"
            "</dl>"
        )

    dados_veiculo = (
        "<dl>"
        f"<div><dt>ID</dt><dd>{vid}</dd></div>"
        f"<div><dt>Marca</dt><dd>{e(veiculo['marca'])}</dd></div>"
        f"<div><dt>Modelo</dt><dd>{e(veiculo['modelo'])}</dd></div>"
        f"<div><dt>Ano</dt><dd>{e(veiculo['ano'])}</dd></div>"
        f"<div><dt>Cor</dt><dd>{e(veiculo['cor'])}</dd></div>"
        f"<div><dt>Combustível</dt><dd>{e(veiculo['combustivel'])}</dd></div>"
        f"<div><dt>Placa</dt><dd>{e(veiculo['placa'])}</dd></div>"
        "</dl>"
    )

    excluir = (
        f'<form method="post" action="/veiculos/{vid}/excluir" '
        'onsubmit="return confirm(\'Excluir este veículo e todos os seus registros?\');">'
        '<button class="botao perigo" type="submit">Excluir veículo</button></form>'
    )

    conteudo = (
        cabecalho_veiculo(veiculo, "resumo")
        + f'<div class="cartoes">{cartoes_gastos}</div>'
        + f'<div class="cartoes">{cartoes_registros}</div>'
        + f'<h2>Última manutenção</h2><div class="painel">{bloco_ultima}</div>'
        + f'<h2>Dados do veículo</h2><div class="painel">{dados_veiculo}</div>'
        + excluir
    )
    return layout(descricao_veiculo(veiculo), conteudo, "veiculos", mensagem)


# ---------------------------------------------------------------- Abastecimentos

def pagina_abastecimentos(dados, veiculo, valores=None, erros=None, mensagem=""):
    vid = veiculo["id"]
    hoje = date.today().isoformat()
    if valores is None:
        valores = {"data": hoje, "km": str(veiculo["km"]), "litros": "", "valor": "",
                   "combustivel": veiculo["combustivel"]}

    campos = (
        campo("data", "Data", valores.get("data", hoje), "date", f'max="{hoje}" required')
        + campo("km", "Quilometragem (km)", valores.get("km", ""), "number", 'min="0" required')
        + campo("litros", "Litros abastecidos", valores.get("litros", ""), "text",
                'inputmode="decimal" placeholder="40,5" required')
        + campo("valor", "Valor total pago (R$)", valores.get("valor", ""), "text",
                'inputmode="decimal" placeholder="240,00" required')
        + seletor("combustivel", "Combustível", COMBUSTIVEIS_ABASTECIMENTO,
                  valores.get("combustivel", ""))
    )
    formulario = (
        f'<form class="painel formulario" method="post" action="/veiculos/{vid}/abastecimentos">'
        '<p class="dica">O preço por litro é calculado automaticamente. Se a quilometragem for '
        "menor que a atual, o registro é salvo mas a km atual do veículo não muda.</p>"
        f'<div class="grade">{campos}</div>'
        '<button class="botao" type="submit">Registrar abastecimento</button></form>'
    )

    registros = abastecimentos_do_veiculo(dados, vid)
    if registros:
        ordenados = sorted(registros, key=lambda a: (a["data"], a["id"]), reverse=True)
        linhas = [[a["id"], formatar_data(a["data"]), formatar_km(a["km"]),
                   formatar_numero(a["litros"]) + " L", formatar_moeda(a["valor_total"]),
                   formatar_moeda(a["preco_por_litro"], 3), e(a["combustivel"])]
                  for a in ordenados]
        historico = tabela(["ID", "Data", "Km", "Litros", "Valor", "R$/litro", "Combustível"],
                           linhas)
        consumo = calcular_consumo_medio(registros)
        texto_consumo = "dados insuficientes (mínimo de 2 abastecimentos)" if consumo is None \
            else f"{formatar_numero(consumo)} km/l"
        chips = (
            f'<span class="chip">{len(registros)} abastecimento(s)</span>'
            f'<span class="chip">{formatar_numero(sum(a["litros"] for a in registros))} L no total</span>'
            f'<span class="chip">{formatar_moeda(sum(a["valor_total"] for a in registros))} gastos</span>'
            f'<span class="chip">Consumo médio: {texto_consumo}</span>'
        )
        historico = f'<div class="chips">{chips}</div>{historico}'
    else:
        historico = '<div class="vazio">Nenhum abastecimento registrado para este veículo.</div>'

    conteudo = (cabecalho_veiculo(veiculo, "abastecimentos") + lista_erros(erros or [])
                + "<h2>Novo abastecimento</h2>" + formulario
                + "<h2>Histórico</h2>" + historico)
    return layout("Abastecimentos", conteudo, "veiculos", mensagem)


# ---------------------------------------------------------------- Manutenções

def pagina_manutencoes(dados, veiculo, valores=None, erros=None, mensagem=""):
    vid = veiculo["id"]
    hoje = date.today().isoformat()
    if valores is None:
        valores = {"data": hoje, "km": str(veiculo["km"]), "tipo": TIPOS_MANUTENCAO[0],
                   "descricao": "", "valor": ""}

    campos = (
        campo("data", "Data", valores.get("data", hoje), "date", f'max="{hoje}" required')
        + campo("km", "Quilometragem (km)", valores.get("km", ""), "number", 'min="0" required')
        + seletor("tipo", "Tipo de manutenção", TIPOS_MANUTENCAO, valores.get("tipo", ""))
        + campo("descricao", "Descrição (obrigatória em \"Outros\")",
                valores.get("descricao", ""))
        + campo("valor", "Valor (R$)", valores.get("valor", ""), "text",
                'inputmode="decimal" placeholder="350,00" required')
    )
    formulario = (
        f'<form class="painel formulario" method="post" action="/veiculos/{vid}/manutencoes">'
        f'<div class="grade">{campos}</div>'
        '<button class="botao" type="submit">Registrar manutenção</button></form>'
    )

    registros = manutencoes_do_veiculo(dados, vid)
    if registros:
        ordenados = sorted(registros, key=lambda m: (m["data"], m["id"]), reverse=True)
        linhas = [[m["id"], formatar_data(m["data"]), formatar_km(m["km"]), e(m["tipo"]),
                   e(m["descricao"] or "-"), formatar_moeda(m["valor"])] for m in ordenados]
        chips = (f'<span class="chip">{len(registros)} manutenção(ões)</span>'
                 f'<span class="chip">{formatar_moeda(sum(m["valor"] for m in registros))} gastos</span>')
        historico = (f'<div class="chips">{chips}</div>'
                     + tabela(["ID", "Data", "Km", "Tipo", "Descrição", "Valor"], linhas))
    else:
        historico = '<div class="vazio">Nenhuma manutenção registrada para este veículo.</div>'

    conteudo = (cabecalho_veiculo(veiculo, "manutencoes") + lista_erros(erros or [])
                + "<h2>Nova manutenção</h2>" + formulario
                + "<h2>Histórico</h2>" + historico)
    return layout("Manutenções", conteudo, "veiculos", mensagem)


# ---------------------------------------------------------------- Gastos

def pagina_gastos(dados, veiculo, valores=None, erros=None, mensagem=""):
    vid = veiculo["id"]
    hoje = date.today().isoformat()
    if valores is None:
        valores = {"data": hoje, "categoria": "Seguro", "descricao": "", "valor": ""}

    campos = (
        campo("data", "Data", valores.get("data", hoje), "date", f'max="{hoje}" required')
        + seletor("categoria", "Categoria", CATEGORIAS, valores.get("categoria", ""))
        + campo("descricao", "Descrição", valores.get("descricao", ""), extra="required")
        + campo("valor", "Valor (R$)", valores.get("valor", ""), "text",
                'inputmode="decimal" placeholder="120,00" required')
    )
    formulario = (
        f'<form class="painel formulario" method="post" action="/veiculos/{vid}/gastos">'
        '<p class="dica">Abastecimentos e manutenções registrados nas outras abas já entram '
        "aqui automaticamente. Use este formulário para seguro, impostos, lavagem etc.</p>"
        f'<div class="grade">{campos}</div>'
        '<button class="botao" type="submit">Registrar gasto</button></form>'
    )

    origens = {"manual": "Manual", "abastecimento": "Abastecimento", "manutencao": "Manutenção"}
    registros = gastos_do_veiculo(dados, vid)
    if registros:
        ordenados = sorted(registros, key=lambda g: (g["data"], g["id"]), reverse=True)
        linhas = [[g["id"], formatar_data(g["data"]), e(g["categoria"]), e(g["descricao"]),
                   formatar_moeda(g["valor"]),
                   f'<span class="etiqueta">{origens.get(g.get("origem"), "Manual")}</span>']
                  for g in ordenados]
        chips = ""
        for categoria in CATEGORIAS:
            subtotal = total_gastos(dados, vid, categoria)
            if subtotal > 0:
                chips += f'<span class="chip">{categoria}: {formatar_moeda(subtotal)}</span>'
        chips += f'<span class="chip"><strong>Total: {formatar_moeda(total_gastos(dados, vid))}</strong></span>'
        historico = (f'<div class="chips">{chips}</div>'
                     + tabela(["ID", "Data", "Categoria", "Descrição", "Valor", "Origem"], linhas))
    else:
        historico = '<div class="vazio">Nenhum gasto registrado para este veículo.</div>'

    conteudo = (cabecalho_veiculo(veiculo, "gastos") + lista_erros(erros or [])
                + "<h2>Novo gasto</h2>" + formulario
                + "<h2>Histórico</h2>" + historico)
    return layout("Gastos", conteudo, "veiculos", mensagem)
