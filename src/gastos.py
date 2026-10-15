"""Registro e consulta de gastos dos veículos."""

from storage import gerar_id, salvar_dados
from utils import (
    confirmar,
    cortar,
    formatar_data,
    formatar_moeda,
    ler_data,
    ler_decimal,
    ler_opcao_lista,
    ler_texto,
    titulo,
)
from veiculos import descricao_veiculo, escolher_veiculo

CATEGORIAS = ["Combustível", "Manutenção", "Seguro", "Impostos", "Lavagem", "Outros"]


def criar_gasto(dados, veiculo_id, data, categoria, descricao, valor,
                origem="manual", origem_id=None):
    """Adiciona um gasto à lista (quem chama é responsável por salvar)."""
    gasto = {
        "id": gerar_id(dados["gastos"]),
        "veiculo_id": veiculo_id,
        "data": data,
        "categoria": categoria,
        "descricao": descricao,
        "valor": round(valor, 2),
        "origem": origem,          # "manual", "abastecimento" ou "manutencao"
        "origem_id": origem_id,
    }
    dados["gastos"].append(gasto)
    return gasto


def gastos_do_veiculo(dados, veiculo_id):
    return [g for g in dados["gastos"] if g["veiculo_id"] == veiculo_id]


def total_gastos(dados, veiculo_id, categoria=None):
    """Soma os gastos de um veículo (opcionalmente só de uma categoria)."""
    total = 0.0
    for gasto in gastos_do_veiculo(dados, veiculo_id):
        if categoria is None or gasto["categoria"] == categoria:
            total += gasto["valor"]
    return total


def registrar_gasto(dados):
    titulo("Registrar gasto")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return

    print(f"\nVeículo selecionado: {descricao_veiculo(veiculo)}")
    data = ler_data("Data do gasto")
    categoria = ler_opcao_lista("Categoria:", CATEGORIAS)

    if categoria in ("Combustível", "Manutenção"):
        print("\nAtenção: abastecimentos (opção 6) e manutenções (opção 8) já "
              "geram gastos automaticamente.")
        if not confirmar("Registrar este gasto manualmente mesmo assim?"):
            print("Operação cancelada.")
            return

    descricao = ler_texto("Descrição")
    valor = ler_decimal("Valor (R$)", maior_que_zero=True)

    criar_gasto(dados, veiculo["id"], data, categoria, descricao, valor)
    if salvar_dados(dados):
        print("\nGasto registrado com sucesso!")


def ver_gastos(dados):
    titulo("Gastos do veículo")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return

    gastos = gastos_do_veiculo(dados, veiculo["id"])
    print(f"\nGastos de: {descricao_veiculo(veiculo)}")
    if not gastos:
        print("\nNenhum gasto registrado para este veículo.")
        return

    gastos = sorted(gastos, key=lambda g: (g["data"], g["id"]), reverse=True)
    print(f"\n{'ID':<4}{'Data':<12}{'Categoria':<13}{'Descrição':<34}{'Valor':>14}")
    print("-" * 77)
    for g in gastos:
        print(f"{g['id']:<4}{formatar_data(g['data']):<12}{g['categoria']:<13}"
              f"{cortar(g['descricao'], 33):<34}{formatar_moeda(g['valor']):>14}")

    print("\nTotal por categoria:")
    for categoria in CATEGORIAS:
        subtotal = total_gastos(dados, veiculo["id"], categoria)
        if subtotal > 0:
            print(f"  {categoria:<13}: {formatar_moeda(subtotal)}")
    print(f"\nTOTAL GERAL: {formatar_moeda(total_gastos(dados, veiculo['id']))}")
