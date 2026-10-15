"""CarManager - sistema de gerenciamento de veículos (terminal).

Execute com:  python src/main.py
"""

from abastecimentos import historico_abastecimentos, registrar_abastecimento
from gastos import registrar_gasto, ver_gastos
from manutencoes import historico_manutencoes, registrar_manutencao
from resumo import resumo_veiculo
from storage import carregar_dados
from utils import pausar
from veiculos import (
    cadastrar_veiculo,
    consultar_veiculo,
    editar_veiculo,
    excluir_veiculo,
    listar_veiculos,
)

# Número da opção -> (texto do menu, função que executa)
OPCOES = {
    "1": ("Cadastrar veículo", cadastrar_veiculo),
    "2": ("Listar veículos", listar_veiculos),
    "3": ("Consultar veículo", consultar_veiculo),
    "4": ("Editar veículo", editar_veiculo),
    "5": ("Excluir veículo", excluir_veiculo),
    "6": ("Registrar abastecimento", registrar_abastecimento),
    "7": ("Ver histórico de abastecimentos", historico_abastecimentos),
    "8": ("Registrar manutenção", registrar_manutencao),
    "9": ("Ver histórico de manutenções", historico_manutencoes),
    "10": ("Registrar gasto", registrar_gasto),
    "11": ("Ver gastos do veículo", ver_gastos),
    "12": ("Ver resumo do veículo", resumo_veiculo),
}


def exibir_menu():
    print()
    print("=" * 56)
    print("CARMANAGER - Gerenciador de Veículos".center(56))
    print("=" * 56)
    for numero, (texto, _funcao) in OPCOES.items():
        print(f"  {numero:>2} - {texto}")
    print("   0 - Sair")
    print("-" * 56)


def main():
    dados = carregar_dados()
    print("Bem-vindo ao CarManager!")

    while True:
        try:
            exibir_menu()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "0":
                print("\nDados salvos. Até logo!")
                break

            if opcao not in OPCOES:
                print("\nOpção inválida. Digite um número do menu.")
                continue

            OPCOES[opcao][1](dados)
            pausar()
        except KeyboardInterrupt:
            print("\n\nOperação interrompida. Voltando ao menu...")
        except EOFError:
            print("\n\nEntrada encerrada. Até logo!")
            break
        except Exception as erro:  # rede de segurança: o programa não fecha
            print(f"\nOcorreu um erro inesperado: {erro}")


if __name__ == "__main__":
    main()
