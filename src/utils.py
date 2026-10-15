"""Funções auxiliares: leitura/validação de entradas e formatação de valores."""

import math
from datetime import date, datetime


# ---------------------------------------------------------------- Tela

def pausar():
    input("\nPressione ENTER para continuar...")


def titulo(texto):
    print()
    print("=" * 56)
    print(texto.upper().center(56))
    print("=" * 56)


def cortar(texto, tamanho):
    """Corta textos longos para caberem nas tabelas."""
    texto = str(texto)
    if len(texto) <= tamanho:
        return texto
    return texto[: tamanho - 3] + "..."


# ---------------------------------------------------------------- Entradas

def ler_texto(mensagem, obrigatorio=True, padrao=None):
    """Lê um texto. Com 'padrao', ENTER mantém o valor padrão."""
    while True:
        sufixo = f" [{padrao}]" if padrao not in (None, "") else ""
        valor = input(f"{mensagem}{sufixo}: ").strip()
        if valor == "":
            if padrao is not None:
                return padrao
            if obrigatorio:
                print("  Erro: este campo não pode ficar vazio.")
                continue
        return valor


def ler_inteiro(mensagem, minimo=None, maximo=None, padrao=None):
    """Lê um número inteiro dentro dos limites informados."""
    while True:
        sufixo = f" [{padrao}]" if padrao is not None else ""
        valor = input(f"{mensagem}{sufixo}: ").strip()
        if valor == "" and padrao is not None:
            return padrao
        try:
            numero = int(valor)
        except ValueError:
            print("  Erro: digite um número inteiro (ex.: 45000).")
            continue
        if minimo is not None and numero < minimo:
            print(f"  Erro: o valor mínimo é {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"  Erro: o valor máximo é {maximo}.")
            continue
        return numero


def ler_decimal(mensagem, minimo=None, maior_que_zero=False):
    """Lê um número decimal. Aceita vírgula ou ponto (ex.: 45,90)."""
    while True:
        valor = input(f"{mensagem}: ").strip().replace(" ", "")
        if "," in valor:
            # "1.234,56" -> "1234.56"
            valor = valor.replace(".", "").replace(",", ".")
        try:
            numero = float(valor)
        except ValueError:
            print("  Erro: digite um número válido (ex.: 45,90).")
            continue
        if not math.isfinite(numero):
            print("  Erro: digite um número válido (ex.: 45,90).")
            continue
        if maior_que_zero and numero <= 0:
            print("  Erro: o valor deve ser maior que zero.")
            continue
        if minimo is not None and numero < minimo:
            print(f"  Erro: o valor mínimo é {minimo}.")
            continue
        return numero


def ler_data(mensagem):
    """Lê uma data no formato DD/MM/AAAA. ENTER usa a data de hoje.

    Devolve a data como texto 'AAAA-MM-DD' (formato usado no JSON).
    """
    hoje = date.today()
    while True:
        valor = input(f"{mensagem} (DD/MM/AAAA, ENTER = hoje): ").strip()
        if valor == "":
            return hoje.isoformat()
        try:
            data = datetime.strptime(valor, "%d/%m/%Y").date()
        except ValueError:
            print("  Erro: data inválida. Use o formato DD/MM/AAAA (ex.: 25/03/2025).")
            continue
        if data > hoje:
            print("  Erro: a data não pode estar no futuro.")
            continue
        if data.year < 1950:
            print("  Erro: a data é muito antiga.")
            continue
        return data.isoformat()


def ler_opcao_lista(titulo_lista, opcoes, padrao=None):
    """Mostra uma lista numerada e devolve a opção escolhida (o texto)."""
    print(f"\n{titulo_lista}")
    for numero, opcao in enumerate(opcoes, start=1):
        print(f"  {numero} - {opcao}")
    indice_padrao = opcoes.index(padrao) + 1 if padrao in opcoes else None
    escolha = ler_inteiro("Escolha o número", 1, len(opcoes), padrao=indice_padrao)
    return opcoes[escolha - 1]


def confirmar(mensagem):
    """Pergunta sim/não. Devolve True para 's'."""
    while True:
        resposta = input(f"{mensagem} (s/n): ").strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("  Erro: responda com 's' ou 'n'.")


# ---------------------------------------------------------------- Formatação

def formatar_numero(valor, casas=2):
    """1234.5 -> '1.234,50' (padrão brasileiro)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_moeda(valor, casas=2):
    return f"R$ {formatar_numero(valor, casas)}"


def formatar_km(km):
    return f"{formatar_numero(km, 0)} km"


def formatar_data(data_iso):
    """'2025-03-25' -> '25/03/2025'."""
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(data_iso)
