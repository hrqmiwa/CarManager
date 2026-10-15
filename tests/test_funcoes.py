"""Testes automáticos das funções principais do CarManager.

Execute na pasta CarManager com:
    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

# Permite importar os módulos que ficam na pasta src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from abastecimentos import calcular_consumo_medio  # noqa: E402
from gastos import criar_gasto, total_gastos  # noqa: E402
from manutencoes import ultima_manutencao  # noqa: E402
from storage import dados_vazios, gerar_id  # noqa: E402
from utils import formatar_data, formatar_moeda, formatar_numero  # noqa: E402
from veiculos import normalizar_placa  # noqa: E402


class TestPlaca(unittest.TestCase):
    def test_placa_antiga_com_hifen(self):
        self.assertEqual(normalizar_placa("abc-1234"), "ABC-1234")

    def test_placa_antiga_sem_hifen(self):
        self.assertEqual(normalizar_placa("abc1234"), "ABC-1234")

    def test_placa_mercosul(self):
        self.assertEqual(normalizar_placa("abc1d23"), "ABC1D23")

    def test_placa_invalida(self):
        self.assertIsNone(normalizar_placa("123"))
        self.assertIsNone(normalizar_placa("ABCD-123"))


class TestConsumoMedio(unittest.TestCase):
    def test_sem_dados_suficientes(self):
        self.assertIsNone(calcular_consumo_medio([]))
        um = [{"id": 1, "km": 1000, "data": "2026-01-01", "litros": 40}]
        self.assertIsNone(calcular_consumo_medio(um))

    def test_calculo_com_dois_abastecimentos(self):
        registros = [
            {"id": 1, "km": 45500, "data": "2026-09-10", "litros": 40.0},
            {"id": 2, "km": 46100, "data": "2026-10-01", "litros": 36.5},
        ]
        # 600 km rodados / 36,5 litros
        self.assertAlmostEqual(calcular_consumo_medio(registros), 600 / 36.5)

    def test_mesma_quilometragem(self):
        registros = [
            {"id": 1, "km": 1000, "data": "2026-01-01", "litros": 30},
            {"id": 2, "km": 1000, "data": "2026-01-02", "litros": 30},
        ]
        self.assertIsNone(calcular_consumo_medio(registros))


class TestGastos(unittest.TestCase):
    def setUp(self):
        self.dados = dados_vazios()
        criar_gasto(self.dados, 1, "2026-10-01", "Combustível", "Abastecimento", 200.0)
        criar_gasto(self.dados, 1, "2026-10-02", "Seguro", "Parcela", 100.5)
        criar_gasto(self.dados, 2, "2026-10-03", "Lavagem", "Outro carro", 50.0)

    def test_total_por_veiculo(self):
        self.assertAlmostEqual(total_gastos(self.dados, 1), 300.5)
        self.assertAlmostEqual(total_gastos(self.dados, 2), 50.0)

    def test_total_por_categoria(self):
        self.assertAlmostEqual(total_gastos(self.dados, 1, "Combustível"), 200.0)
        self.assertAlmostEqual(total_gastos(self.dados, 1, "Manutenção"), 0.0)


class TestManutencao(unittest.TestCase):
    def test_sem_manutencoes(self):
        self.assertIsNone(ultima_manutencao([]))

    def test_ultima_por_data(self):
        lista = [
            {"id": 1, "data": "2026-01-10", "km": 10000},
            {"id": 2, "data": "2026-08-05", "km": 20000},
            {"id": 3, "data": "2026-03-01", "km": 15000},
        ]
        self.assertEqual(ultima_manutencao(lista)["id"], 2)


class TestAuxiliares(unittest.TestCase):
    def test_gerar_id(self):
        self.assertEqual(gerar_id([]), 1)
        self.assertEqual(gerar_id([{"id": 1}, {"id": 5}]), 6)

    def test_formatacao(self):
        self.assertEqual(formatar_numero(1234.5), "1.234,50")
        self.assertEqual(formatar_moeda(219), "R$ 219,00")
        self.assertEqual(formatar_data("2026-10-05"), "05/10/2026")


if __name__ == "__main__":
    unittest.main()
