"""Validação dos campos dos formulários da versão web.

Cada função devolve (valor, erro): se der certo, erro é None;
se der errado, valor é None e erro traz a mensagem para o usuário.
"""

import math
from datetime import date, datetime


def texto(valor, campo, obrigatorio=True):
    valor = (valor or "").strip()
    if obrigatorio and not valor:
        return None, f"{campo}: este campo não pode ficar vazio."
    return valor, None


def inteiro(valor, campo, minimo=None, maximo=None):
    try:
        numero = int((valor or "").strip())
    except ValueError:
        return None, f"{campo}: digite um número inteiro (ex.: 45000)."
    if minimo is not None and numero < minimo:
        return None, f"{campo}: o valor mínimo é {minimo}."
    if maximo is not None and numero > maximo:
        return None, f"{campo}: o valor máximo é {maximo}."
    return numero, None


def decimal(valor, campo, minimo=None, maior_que_zero=False):
    """Aceita vírgula ou ponto (ex.: 45,90 ou 1.234,56)."""
    texto_numero = (valor or "").strip().replace(" ", "")
    if "," in texto_numero:
        texto_numero = texto_numero.replace(".", "").replace(",", ".")
    try:
        numero = float(texto_numero)
    except ValueError:
        return None, f"{campo}: digite um número válido (ex.: 45,90)."
    if not math.isfinite(numero):
        return None, f"{campo}: digite um número válido (ex.: 45,90)."
    if maior_que_zero and numero <= 0:
        return None, f"{campo}: o valor deve ser maior que zero."
    if minimo is not None and numero < minimo:
        return None, f"{campo}: o valor mínimo é {minimo}."
    return numero, None


def data(valor, campo):
    """Aceita AAAA-MM-DD (campo de data do navegador) ou DD/MM/AAAA.

    Devolve o texto 'AAAA-MM-DD'.
    """
    valor = (valor or "").strip()
    if not valor:
        return None, f"{campo}: informe a data."
    resultado = None
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            resultado = datetime.strptime(valor, formato).date()
            break
        except ValueError:
            continue
    if resultado is None:
        return None, f"{campo}: data inválida."
    if resultado > date.today():
        return None, f"{campo}: a data não pode estar no futuro."
    if resultado.year < 1950:
        return None, f"{campo}: a data é muito antiga."
    return resultado.isoformat(), None


def opcao(valor, campo, opcoes):
    if valor not in opcoes:
        return None, f"{campo}: escolha uma das opções da lista."
    return valor, None


def coletar(erros, resultado):
    """Guarda o erro (se houver) na lista e devolve só o valor."""
    valor, erro = resultado
    if erro:
        erros.append(erro)
    return valor
