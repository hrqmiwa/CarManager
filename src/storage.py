"""Salvamento e carregamento dos dados em um arquivo JSON.

O arquivo fica em CarManager/data/dados.json (a pasta é criada sozinha).
"""

import json
from pathlib import Path

# Caminho calculado a partir deste arquivo, então funciona de qualquer pasta.
PASTA_RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_DADOS = PASTA_RAIZ / "data" / "dados.json"


def dados_vazios():
    """Estrutura inicial (sem nenhum registro)."""
    return {"veiculos": [], "abastecimentos": [], "manutencoes": [], "gastos": []}


def carregar_dados():
    """Lê o JSON. Se não existir, ou estiver corrompido, começa do zero."""
    if not ARQUIVO_DADOS.exists():
        return dados_vazios()

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, dict):
            raise ValueError("formato inesperado")
    except (ValueError, OSError):
        # ValueError cobre JSON inválido (json.JSONDecodeError) e erros de texto.
        print("Aviso: o arquivo de dados está ilegível. Um novo será criado.")
        try:
            ARQUIVO_DADOS.replace(ARQUIVO_DADOS.with_name("dados_corrompido.json"))
        except OSError:
            pass
        return dados_vazios()

    # Garante que todas as listas existam.
    for chave, valor in dados_vazios().items():
        if not isinstance(dados.get(chave), list):
            dados[chave] = valor
    return dados


def salvar_dados(dados):
    """Grava os dados no JSON. Devolve True se deu certo, False se falhou."""
    try:
        ARQUIVO_DADOS.parent.mkdir(parents=True, exist_ok=True)
        temporario = ARQUIVO_DADOS.with_suffix(".tmp")
        with open(temporario, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        temporario.replace(ARQUIVO_DADOS)
        return True
    except OSError as erro:
        print(f"Erro ao salvar os dados: {erro}")
        return False


def gerar_id(registros):
    """Próximo ID disponível para uma lista de registros."""
    if not registros:
        return 1
    return max(registro["id"] for registro in registros) + 1
