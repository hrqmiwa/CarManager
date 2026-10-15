"""Testes da validação dos formulários web e das funções compartilhadas.

Execute na pasta CarManager com:
    python -m unittest discover -s tests -v
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import web_validacao as val  # noqa: E402
from abastecimentos import criar_abastecimento  # noqa: E402
from manutencoes import criar_manutencao  # noqa: E402
from paginas import e  # noqa: E402
from storage import dados_vazios  # noqa: E402
from veiculos import remover_veiculo  # noqa: E402


class TestValidacaoWeb(unittest.TestCase):
    def test_inteiro(self):
        self.assertEqual(val.inteiro("45000", "Km", 0), (45000, None))
        self.assertIsNone(val.inteiro("abc", "Km")[0])
        self.assertIsNotNone(val.inteiro("-1", "Km", 0)[1])

    def test_decimal_aceita_virgula(self):
        self.assertEqual(val.decimal("45,90", "Valor"), (45.9, None))
        self.assertEqual(val.decimal("1.234,56", "Valor"), (1234.56, None))

    def test_decimal_invalido(self):
        self.assertIsNotNone(val.decimal("abc", "Valor")[1])
        self.assertIsNotNone(val.decimal("nan", "Valor")[1])
        self.assertIsNotNone(val.decimal("0", "Valor", maior_que_zero=True)[1])

    def test_data(self):
        self.assertEqual(val.data("2026-03-25", "Data"), ("2026-03-25", None))
        self.assertEqual(val.data("25/03/2026", "Data"), ("2026-03-25", None))
        self.assertIsNotNone(val.data("2099-01-01", "Data")[1])   # futuro
        self.assertIsNotNone(val.data("32/13/2026", "Data")[1])   # inválida
        self.assertIsNotNone(val.data("", "Data")[1])             # vazia

    def test_opcao(self):
        self.assertEqual(val.opcao("Flex", "Combustível", ["Flex", "Diesel"]), ("Flex", None))
        self.assertIsNotNone(val.opcao("Água", "Combustível", ["Flex", "Diesel"])[1])

    def test_coletar(self):
        erros = []
        self.assertEqual(val.coletar(erros, (10, None)), 10)
        self.assertIsNone(val.coletar(erros, (None, "deu erro")))
        self.assertEqual(erros, ["deu erro"])


class TestSeguranca(unittest.TestCase):
    def test_escape_de_html(self):
        self.assertEqual(e("<script>"), "&lt;script&gt;")
        self.assertEqual(e('a"b'), "a&quot;b")


class TestFuncoesCompartilhadas(unittest.TestCase):
    def setUp(self):
        self.dados = dados_vazios()
        self.veiculo = {"id": 1, "marca": "Fiat", "modelo": "Argo", "ano": 2020,
                        "cor": "Branca", "km": 1000, "combustivel": "Flex",
                        "placa": "ABC-1234"}
        self.dados["veiculos"].append(self.veiculo)

    def test_abastecimento_cria_gasto_e_atualiza_km(self):
        a = criar_abastecimento(self.dados, self.veiculo, "2026-10-01", 1500, 40.0, 240.0,
                                "Gasolina")
        self.assertEqual(a["preco_por_litro"], 6.0)
        self.assertEqual(len(self.dados["gastos"]), 1)
        self.assertEqual(self.dados["gastos"][0]["categoria"], "Combustível")
        self.assertEqual(self.veiculo["km"], 1500)

    def test_km_menor_nao_diminui_km_do_veiculo(self):
        criar_abastecimento(self.dados, self.veiculo, "2026-10-01", 500, 10.0, 60.0, "Etanol")
        self.assertEqual(self.veiculo["km"], 1000)

    def test_manutencao_cria_gasto(self):
        criar_manutencao(self.dados, self.veiculo, "2026-10-05", 1200, "Freios", "", 300.0)
        self.assertEqual(len(self.dados["manutencoes"]), 1)
        self.assertEqual(self.dados["gastos"][0]["categoria"], "Manutenção")
        self.assertEqual(self.dados["gastos"][0]["descricao"], "Freios")

    def test_remover_veiculo_apaga_registros(self):
        criar_abastecimento(self.dados, self.veiculo, "2026-10-01", 1500, 40.0, 240.0,
                            "Gasolina")
        criar_manutencao(self.dados, self.veiculo, "2026-10-05", 1500, "Revisão", "", 500.0)
        remover_veiculo(self.dados, 1)
        for chave in ("veiculos", "abastecimentos", "manutencoes", "gastos"):
            self.assertEqual(self.dados[chave], [])


if __name__ == "__main__":
    unittest.main()
