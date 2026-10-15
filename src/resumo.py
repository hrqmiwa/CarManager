"""Resumo geral de um veículo."""

from abastecimentos import abastecimentos_do_veiculo, calcular_consumo_medio
from gastos import total_gastos
from manutencoes import manutencoes_do_veiculo, ultima_manutencao
from utils import formatar_data, formatar_km, formatar_moeda, formatar_numero, titulo
from veiculos import escolher_veiculo, exibir_veiculo


def resumo_veiculo(dados):
    titulo("Resumo do veículo")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return

    vid = veiculo["id"]
    abastecimentos = abastecimentos_do_veiculo(dados, vid)
    manutencoes = manutencoes_do_veiculo(dados, vid)
    ultima = ultima_manutencao(manutencoes)
    consumo = calcular_consumo_medio(abastecimentos)

    print("\n--- DADOS DO VEÍCULO ---")
    exibir_veiculo(veiculo)

    print("\n--- QUILOMETRAGEM ---")
    print(f"  Quilometragem atual: {formatar_km(veiculo['km'])}")

    print("\n--- GASTOS ---")
    print(f"  Total gasto..........: {formatar_moeda(total_gastos(dados, vid))}")
    print(f"  Gasto com combustível: {formatar_moeda(total_gastos(dados, vid, 'Combustível'))}")
    print(f"  Gasto com manutenção.: {formatar_moeda(total_gastos(dados, vid, 'Manutenção'))}")

    print("\n--- REGISTROS ---")
    print(f"  Abastecimentos: {len(abastecimentos)}")
    print(f"  Manutenções...: {len(manutencoes)}")
    if consumo is None:
        print("  Consumo médio.: dados insuficientes")
    else:
        print(f"  Consumo médio.: {formatar_numero(consumo)} km/l")

    print("\n--- ÚLTIMA MANUTENÇÃO ---")
    if ultima is None:
        print("  Nenhuma manutenção registrada.")
    else:
        print(f"  Data......: {formatar_data(ultima['data'])}")
        print(f"  Tipo......: {ultima['tipo']}")
        print(f"  Quilometragem: {formatar_km(ultima['km'])}")
        print(f"  Descrição.: {ultima['descricao'] or '-'}")
        print(f"  Valor.....: {formatar_moeda(ultima['valor'])}")
