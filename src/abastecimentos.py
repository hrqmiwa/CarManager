"""Registro e histórico de abastecimentos."""

from gastos import criar_gasto
from storage import gerar_id, salvar_dados
from utils import (
    formatar_data,
    formatar_km,
    formatar_moeda,
    formatar_numero,
    ler_data,
    ler_decimal,
    ler_inteiro,
    ler_opcao_lista,
    titulo,
)
from veiculos import atualizar_km, confirmar_km, descricao_veiculo, escolher_veiculo

COMBUSTIVEIS_ABASTECIMENTO = ["Gasolina", "Etanol", "Diesel", "GNV"]


def abastecimentos_do_veiculo(dados, veiculo_id):
    return [a for a in dados["abastecimentos"] if a["veiculo_id"] == veiculo_id]


def calcular_consumo_medio(abastecimentos):
    """Estimativa simples de consumo médio (km/l).

    Considera que o tanque é completado em todo abastecimento:
    km rodados entre o primeiro e o último abastecimento dividido pelos
    litros abastecidos depois do primeiro. Precisa de 2 ou mais registros.
    Devolve None se não houver dados suficientes.
    """
    if len(abastecimentos) < 2:
        return None
    ordenados = sorted(abastecimentos, key=lambda a: (a["km"], a["data"], a["id"]))
    distancia = ordenados[-1]["km"] - ordenados[0]["km"]
    litros = sum(a["litros"] for a in ordenados[1:])
    if distancia <= 0 or litros <= 0:
        return None
    return distancia / litros


def criar_abastecimento(dados, veiculo, data, km, litros, valor_total, combustivel):
    """Cria o abastecimento, o gasto correspondente e atualiza a km do veículo.

    Quem chama é responsável por salvar os dados. Usada pelo terminal e pela web.
    """
    abastecimento = {
        "id": gerar_id(dados["abastecimentos"]),
        "veiculo_id": veiculo["id"],
        "data": data,
        "km": km,
        "litros": round(litros, 2),
        "valor_total": round(valor_total, 2),
        "preco_por_litro": round(valor_total / litros, 3),
        "combustivel": combustivel,
    }
    dados["abastecimentos"].append(abastecimento)

    # Todo abastecimento também vira um gasto na categoria "Combustível".
    criar_gasto(
        dados, veiculo["id"], data, "Combustível",
        f"Abastecimento: {formatar_numero(litros)} L de {combustivel}",
        valor_total, origem="abastecimento", origem_id=abastecimento["id"],
    )
    atualizar_km(veiculo, km)
    return abastecimento


def registrar_abastecimento(dados):
    titulo("Registrar abastecimento")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return

    print(f"\nVeículo selecionado: {descricao_veiculo(veiculo)}")
    data = ler_data("Data do abastecimento")
    km = ler_inteiro("Quilometragem no momento (km)", 0)
    if not confirmar_km(veiculo, km):
        print("Operação cancelada.")
        return
    litros = ler_decimal("Litros abastecidos", maior_que_zero=True)
    valor_total = ler_decimal("Valor total pago (R$)", maior_que_zero=True)

    padrao = veiculo["combustivel"] if veiculo["combustivel"] in COMBUSTIVEIS_ABASTECIMENTO else None
    combustivel = ler_opcao_lista("Combustível abastecido:", COMBUSTIVEIS_ABASTECIMENTO,
                                  padrao=padrao)

    preco_litro = valor_total / litros
    criar_abastecimento(dados, veiculo, data, km, litros, valor_total, combustivel)

    if salvar_dados(dados):
        print("\nAbastecimento registrado com sucesso!")
        print(f"Preço por litro: {formatar_moeda(preco_litro, 3)}")
        consumo = calcular_consumo_medio(abastecimentos_do_veiculo(dados, veiculo["id"]))
        if consumo is None:
            print("Consumo médio: ainda não há dados suficientes "
                  "(são necessários 2 abastecimentos).")
        else:
            print(f"Consumo médio estimado: {formatar_numero(consumo)} km/l")


def historico_abastecimentos(dados):
    titulo("Histórico de abastecimentos")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return

    registros = abastecimentos_do_veiculo(dados, veiculo["id"])
    print(f"\nAbastecimentos de: {descricao_veiculo(veiculo)}")
    if not registros:
        print("\nNenhum abastecimento registrado para este veículo.")
        return

    ordenados = sorted(registros, key=lambda a: (a["data"], a["id"]), reverse=True)
    print(f"\n{'ID':<4}{'Data':<12}{'Km':>12}{'Litros':>10}{'Valor':>14}"
          f"{'R$/litro':>11}  {'Combustível'}")
    print("-" * 78)
    for a in ordenados:
        print(f"{a['id']:<4}{formatar_data(a['data']):<12}{formatar_km(a['km']):>12}"
              f"{formatar_numero(a['litros']):>10}{formatar_moeda(a['valor_total']):>14}"
              f"{formatar_numero(a['preco_por_litro'], 3):>11}  {a['combustivel']}")

    total_litros = sum(a["litros"] for a in registros)
    total_valor = sum(a["valor_total"] for a in registros)
    print(f"\nTotal de abastecimentos: {len(registros)}")
    print(f"Total de litros........: {formatar_numero(total_litros)} L")
    print(f"Total gasto............: {formatar_moeda(total_valor)}")

    consumo = calcular_consumo_medio(registros)
    if consumo is None:
        print("Consumo médio..........: dados insuficientes (mínimo de 2 abastecimentos)")
    else:
        print(f"Consumo médio estimado.: {formatar_numero(consumo)} km/l")
