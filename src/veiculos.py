"""Cadastro e gerenciamento de veículos."""

import re
from datetime import date

from storage import gerar_id, salvar_dados
from utils import (
    confirmar,
    cortar,
    formatar_km,
    ler_inteiro,
    ler_opcao_lista,
    ler_texto,
    titulo,
)

COMBUSTIVEIS = ["Gasolina", "Etanol", "Flex", "Diesel", "GNV", "Elétrico", "Híbrido"]
ANO_MINIMO = 1900


# ---------------------------------------------------------------- Auxiliares

def buscar_veiculo(dados, veiculo_id):
    """Devolve o veículo com esse ID, ou None."""
    for veiculo in dados["veiculos"]:
        if veiculo["id"] == veiculo_id:
            return veiculo
    return None


def descricao_veiculo(veiculo):
    return (f"{veiculo['marca']} {veiculo['modelo']} {veiculo['ano']} "
            f"- {veiculo['placa']}")


def normalizar_placa(texto):
    """Aceita ABC-1234 ou ABC1D23 (Mercosul). Devolve a placa ou None."""
    placa = texto.upper().replace("-", "").replace(" ", "")
    if re.fullmatch(r"[A-Z]{3}\d{4}", placa):
        return f"{placa[:3]}-{placa[3:]}"
    if re.fullmatch(r"[A-Z]{3}\d[A-Z]\d{2}", placa):
        return placa
    return None


def ler_placa(dados, ignorar_id=None, padrao=None):
    """Lê uma placa válida e que ainda não exista em outro veículo."""
    while True:
        texto = ler_texto("Placa fictícia (ex.: ABC-1234 ou ABC1D23)", padrao=padrao)
        placa = normalizar_placa(texto)
        if placa is None:
            print("  Erro: formato inválido. Use ABC-1234 ou ABC1D23.")
            continue
        repetida = any(
            v["placa"] == placa and v["id"] != ignorar_id for v in dados["veiculos"]
        )
        if repetida:
            print("  Erro: já existe um veículo com essa placa.")
            continue
        return placa


def imprimir_tabela_veiculos(veiculos):
    print(f"\n{'ID':<4}{'Marca':<13}{'Modelo':<15}{'Ano':<6}{'Cor':<10}"
          f"{'Km':>12}  {'Combustível':<12}{'Placa':<9}")
    print("-" * 82)
    for v in veiculos:
        print(f"{v['id']:<4}{cortar(v['marca'], 12):<13}{cortar(v['modelo'], 14):<15}"
              f"{v['ano']:<6}{cortar(v['cor'], 9):<10}{formatar_km(v['km']):>12}  "
              f"{v['combustivel']:<12}{v['placa']:<9}")


def escolher_veiculo(dados, mensagem="ID do veículo"):
    """Mostra os veículos e pede o ID. Devolve o veículo ou None (cancelado)."""
    if not dados["veiculos"]:
        print("\nNenhum veículo cadastrado. Cadastre um veículo primeiro (opção 1).")
        return None
    imprimir_tabela_veiculos(dados["veiculos"])
    while True:
        veiculo_id = ler_inteiro(f"\n{mensagem} (0 para cancelar)", 0)
        if veiculo_id == 0:
            print("Operação cancelada.")
            return None
        veiculo = buscar_veiculo(dados, veiculo_id)
        if veiculo is not None:
            return veiculo
        print("  Erro: não existe veículo com esse ID.")


def confirmar_km(veiculo, km):
    """Avisa se a km informada é menor que a km atual do veículo."""
    if km < veiculo["km"]:
        print(f"\nAtenção: a quilometragem informada ({formatar_km(km)}) é menor "
              f"que a atual do veículo ({formatar_km(veiculo['km'])}).")
        return confirmar("Deseja continuar mesmo assim?")
    return True


def atualizar_km(veiculo, km):
    """Atualiza a km atual do veículo se a nova for maior."""
    if km > veiculo["km"]:
        veiculo["km"] = km


def remover_veiculo(dados, veiculo_id):
    """Remove o veículo e todos os registros ligados a ele (sem salvar)."""
    dados["veiculos"] = [v for v in dados["veiculos"] if v["id"] != veiculo_id]
    dados["abastecimentos"] = [a for a in dados["abastecimentos"] if a["veiculo_id"] != veiculo_id]
    dados["manutencoes"] = [m for m in dados["manutencoes"] if m["veiculo_id"] != veiculo_id]
    dados["gastos"] = [g for g in dados["gastos"] if g["veiculo_id"] != veiculo_id]


def exibir_veiculo(veiculo):
    print(f"\n  ID.................: {veiculo['id']}")
    print(f"  Marca..............: {veiculo['marca']}")
    print(f"  Modelo.............: {veiculo['modelo']}")
    print(f"  Ano................: {veiculo['ano']}")
    print(f"  Cor................: {veiculo['cor']}")
    print(f"  Quilometragem atual: {formatar_km(veiculo['km'])}")
    print(f"  Combustível........: {veiculo['combustivel']}")
    print(f"  Placa..............: {veiculo['placa']}")


# ---------------------------------------------------------------- Opções do menu

def cadastrar_veiculo(dados):
    titulo("Cadastrar veículo")
    print("Use apenas dados fictícios (a placa também deve ser inventada).\n")

    marca = ler_texto("Marca")
    modelo = ler_texto("Modelo")
    ano = ler_inteiro("Ano", ANO_MINIMO, date.today().year + 1)
    cor = ler_texto("Cor")
    km = ler_inteiro("Quilometragem atual (km)", 0)
    combustivel = ler_opcao_lista("Tipo de combustível:", COMBUSTIVEIS)
    placa = ler_placa(dados)

    veiculo = {
        "id": gerar_id(dados["veiculos"]),
        "marca": marca,
        "modelo": modelo,
        "ano": ano,
        "cor": cor,
        "km": km,
        "combustivel": combustivel,
        "placa": placa,
    }
    dados["veiculos"].append(veiculo)
    if salvar_dados(dados):
        print(f"\nVeículo cadastrado com sucesso! ID: {veiculo['id']}")


def listar_veiculos(dados):
    titulo("Veículos cadastrados")
    if not dados["veiculos"]:
        print("\nNenhum veículo cadastrado.")
        return
    imprimir_tabela_veiculos(dados["veiculos"])
    print(f"\nTotal: {len(dados['veiculos'])} veículo(s).")


def consultar_veiculo(dados):
    titulo("Consultar veículo")
    veiculo = escolher_veiculo(dados)
    if veiculo is None:
        return
    exibir_veiculo(veiculo)


def editar_veiculo(dados):
    titulo("Editar veículo")
    veiculo = escolher_veiculo(dados, "ID do veículo a editar")
    if veiculo is None:
        return

    print("\nPressione ENTER para manter o valor atual.\n")
    # Os novos valores são guardados à parte e só aplicados no final,
    # assim uma edição interrompida não deixa o veículo pela metade.
    novos = {}
    novos["marca"] = ler_texto("Marca", padrao=veiculo["marca"])
    novos["modelo"] = ler_texto("Modelo", padrao=veiculo["modelo"])
    novos["ano"] = ler_inteiro("Ano", ANO_MINIMO, date.today().year + 1,
                               padrao=veiculo["ano"])
    novos["cor"] = ler_texto("Cor", padrao=veiculo["cor"])
    novos["km"] = ler_inteiro("Quilometragem atual (km)", 0, padrao=veiculo["km"])
    novos["combustivel"] = ler_opcao_lista("Tipo de combustível:", COMBUSTIVEIS,
                                           padrao=veiculo["combustivel"])
    novos["placa"] = ler_placa(dados, ignorar_id=veiculo["id"], padrao=veiculo["placa"])

    veiculo.update(novos)
    if salvar_dados(dados):
        print("\nVeículo atualizado com sucesso!")


def excluir_veiculo(dados):
    titulo("Excluir veículo")
    veiculo = escolher_veiculo(dados, "ID do veículo a excluir")
    if veiculo is None:
        return

    vid = veiculo["id"]
    qtd_abast = sum(1 for a in dados["abastecimentos"] if a["veiculo_id"] == vid)
    qtd_manut = sum(1 for m in dados["manutencoes"] if m["veiculo_id"] == vid)
    qtd_gastos = sum(1 for g in dados["gastos"] if g["veiculo_id"] == vid)

    print(f"\nVocê vai excluir: {descricao_veiculo(veiculo)}")
    print(f"Também serão apagados: {qtd_abast} abastecimento(s), "
          f"{qtd_manut} manutenção(ões) e {qtd_gastos} gasto(s).")
    if not confirmar("Tem certeza que deseja excluir?"):
        print("Exclusão cancelada.")
        return

    remover_veiculo(dados, vid)
    if salvar_dados(dados):
        print("\nVeículo excluído com sucesso!")
