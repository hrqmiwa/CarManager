"""Registro e histórico de manutenções."""

from gastos import criar_gasto
from storage import gerar_id, salvar_dados
from utils import (
    cortar,
    formatar_data,
    formatar_km,
    formatar_moeda,
    ler_data,
    ler_decimal,
    ler_inteiro,
    ler_opcao_lista,
    ler_texto,
    titulo,
)
from veiculos import atualizar_km, confirmar_km, descricao_veiculo, escolher_veiculo

TIPOS_MANUTENCAO = ["Troca de óleo", "Revisão", "Troca de pneus", "Freios",
                    "Bateria", "Outros"]


def manutencoes_do_veiculo(dados, veiculo_id):
    return [m for m in dados["manutencoes"] if m["veiculo_id"] == veiculo_id]


def ultima_manutencao(manutencoes):
    """Manutenção mais recente (por data) ou None."""
    if not manutencoes:
        return None
    return max(manutencoes, key=lambda m: (m["data"], m["km"], m["id"]))


def criar_manutencao(dados, veiculo, data, km, tipo, descricao, valor):
    """Cria a manutenção, o gasto correspondente e atualiza a km do veículo.

    Quem chama é responsável por salvar os dados. Usada pelo terminal e pela web.
    """
    manutencao = {
        "id": gerar_id(dados["manutencoes"]),
        "veiculo_id": veiculo["id"],
        "data": data,
        "km": km,
        "tipo": tipo,
        "descricao": descricao,
        "valor": round(valor, 2),
    }
    dados["manutencoes"].append(manutencao)

    # Toda manutenção também vira um gasto na categoria "Manutenção".
    texto_gasto = f"{tipo}: {descricao}" if descricao else tipo
    criar_gasto(dados, veiculo["id"], data, "Manutenção", texto_gasto, valor,
                origem="manutencao", origem_id=manutencao["id"])
    atualizar_km(veiculo, km)
    return manutencao


def registrar_manutencao(dados):
    titulo("Registrar manutenção")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return

    print(f"\nVeículo selecionado: {descricao_veiculo(veiculo)}")
    data = ler_data("Data da manutenção")
    km = ler_inteiro("Quilometragem no momento (km)", 0)
    if not confirmar_km(veiculo, km):
        print("Operação cancelada.")
        return
    tipo = ler_opcao_lista("Tipo de manutenção:", TIPOS_MANUTENCAO)
    # A descrição só é obrigatória quando o tipo é "Outros".
    descricao = ler_texto("Descrição (ENTER para deixar em branco)" if tipo != "Outros"
                          else "Descrição", obrigatorio=(tipo == "Outros"))
    valor = ler_decimal("Valor (R$)", minimo=0)

    criar_manutencao(dados, veiculo, data, km, tipo, descricao, valor)

    if salvar_dados(dados):
        print("\nManutenção registrada com sucesso!")


def historico_manutencoes(dados):
    titulo("Histórico de manutenções")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return

    registros = manutencoes_do_veiculo(dados, veiculo["id"])
    print(f"\nManutenções de: {descricao_veiculo(veiculo)}")
    if not registros:
        print("\nNenhuma manutenção registrada para este veículo.")
        return

    ordenados = sorted(registros, key=lambda m: (m["data"], m["id"]), reverse=True)
    print(f"\n{'ID':<4}{'Data':<12}{'Km':>12}  {'Tipo':<16}{'Descrição':<26}{'Valor':>13}")
    print("-" * 85)
    for m in ordenados:
        print(f"{m['id']:<4}{formatar_data(m['data']):<12}{formatar_km(m['km']):>12}  "
              f"{m['tipo']:<16}{cortar(m['descricao'] or '-', 25):<26}"
              f"{formatar_moeda(m['valor']):>13}")

    total = sum(m["valor"] for m in registros)
    print(f"\nTotal de manutenções: {len(registros)}")
    print(f"Total gasto: {formatar_moeda(total)}")
