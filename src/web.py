"""CarManager - versão web (servidor local, somente bibliotecas nativas).

Execute com:   python src/web.py
O navegador abre sozinho em http://127.0.0.1:8000
Para encerrar, volte ao terminal e aperte Ctrl+C.

O servidor só aceita conexões do próprio computador (127.0.0.1) e usa o
mesmo arquivo de dados (data/dados.json) da versão de terminal.
"""

import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import paginas
import web_validacao as val
from abastecimentos import COMBUSTIVEIS_ABASTECIMENTO, criar_abastecimento
from gastos import CATEGORIAS, criar_gasto
from manutencoes import TIPOS_MANUTENCAO, criar_manutencao
from storage import carregar_dados, gerar_id, salvar_dados
from veiculos import (
    ANO_MINIMO,
    COMBUSTIVEIS,
    buscar_veiculo,
    normalizar_placa,
    remover_veiculo,
)

PASTA_STATIC = Path(__file__).resolve().parent / "static"
HOST = "127.0.0.1"
PORTAS = range(8000, 8011)
TAMANHO_MAXIMO_FORM = 100_000


# ---------------------------------------------------------------- Validação dos formulários

def validar_veiculo(dados, form, ignorar_id=None):
    """Devolve (novos_valores, lista_de_erros)."""
    erros = []
    marca = val.coletar(erros, val.texto(form.get("marca"), "Marca"))
    modelo = val.coletar(erros, val.texto(form.get("modelo"), "Modelo"))
    ano = val.coletar(erros, val.inteiro(form.get("ano"), "Ano", ANO_MINIMO,
                                         date.today().year + 1))
    cor = val.coletar(erros, val.texto(form.get("cor"), "Cor"))
    km = val.coletar(erros, val.inteiro(form.get("km"), "Quilometragem", 0))
    combustivel = val.coletar(erros, val.opcao(form.get("combustivel"), "Combustível",
                                               COMBUSTIVEIS))

    placa = normalizar_placa(form.get("placa", ""))
    if placa is None:
        erros.append("Placa: use o formato ABC-1234 ou ABC1D23.")
    elif any(v["placa"] == placa and v["id"] != ignorar_id for v in dados["veiculos"]):
        erros.append("Placa: já existe um veículo com essa placa.")

    novos = {"marca": marca, "modelo": modelo, "ano": ano, "cor": cor, "km": km,
             "combustivel": combustivel, "placa": placa}
    return novos, erros


def valores_do_veiculo(veiculo):
    """Transforma o veículo em textos para preencher o formulário de edição."""
    return {chave: str(veiculo[chave]) for chave in
            ("marca", "modelo", "ano", "cor", "km", "combustivel", "placa")}


# ---------------------------------------------------------------- Servidor

class Handler(BaseHTTPRequestHandler):
    server_version = "CarManager"

    # ----- respostas -----
    def enviar(self, codigo, corpo, tipo="text/html; charset=utf-8"):
        conteudo = corpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)

    def redirecionar(self, destino, mensagem=""):
        if mensagem:
            destino += "?msg=" + quote(mensagem)
        self.send_response(303)
        self.send_header("Location", destino)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def nao_encontrado(self):
        self.enviar(404, paginas.pagina_erro("Página não encontrada",
                                             "O endereço acessado não existe."))

    def salvar_e_redirecionar(self, destino, mensagem):
        if salvar_dados(self.server.dados):
            self.redirecionar(destino, mensagem)
        else:
            self.enviar(500, paginas.pagina_erro("Erro ao salvar",
                                                 "Não foi possível gravar o arquivo de dados."))

    def ler_formulario(self):
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
        except ValueError:
            tamanho = 0
        corpo = self.rfile.read(min(tamanho, TAMANHO_MAXIMO_FORM)).decode("utf-8", "replace")
        campos = parse_qs(corpo, keep_blank_values=True)
        return {nome: valores[0] for nome, valores in campos.items()}

    # ----- entrada -----
    def do_GET(self):
        self.tratar("GET")

    def do_POST(self):
        self.tratar("POST")

    def tratar(self, metodo):
        try:
            url = urlparse(self.path)
            partes = [p for p in url.path.split("/") if p]
            mensagem = parse_qs(url.query).get("msg", [""])[0]
            form = self.ler_formulario() if metodo == "POST" else {}
            self.rotear(metodo, partes, form, mensagem)
        except Exception as erro:  # rede de segurança: o servidor não cai
            self.enviar(500, paginas.pagina_erro("Erro inesperado", str(erro)))

    # ----- rotas -----
    def rotear(self, metodo, partes, form, mensagem):
        dados = self.server.dados

        if metodo == "GET" and partes == ["static", "style.css"]:
            css = (PASTA_STATIC / "style.css").read_text(encoding="utf-8")
            return self.enviar(200, css, "text/css; charset=utf-8")

        if metodo == "GET" and partes == ["static", "app.js"]:
            js = (PASTA_STATIC / "app.js").read_text(encoding="utf-8")
            return self.enviar(200, js, "application/javascript; charset=utf-8")

        if metodo == "GET" and not partes:
            return self.enviar(200, paginas.pagina_inicio(dados, mensagem))

        if partes == ["veiculos"] and metodo == "GET":
            return self.enviar(200, paginas.pagina_veiculos(dados, mensagem))

        if partes == ["veiculos", "novo"]:
            if metodo == "GET":
                return self.enviar(200, paginas.pagina_form_veiculo({}, []))
            return self.post_cadastrar_veiculo(dados, form)

        if len(partes) in (2, 3) and partes[0] == "veiculos" and partes[1].isdigit():
            veiculo = buscar_veiculo(dados, int(partes[1]))
            if veiculo is None:
                return self.nao_encontrado()
            acao = partes[2] if len(partes) == 3 else ""
            if metodo == "GET":
                return self.get_veiculo(dados, veiculo, acao, mensagem)
            return self.post_veiculo(dados, veiculo, acao, form)

        self.nao_encontrado()

    def get_veiculo(self, dados, veiculo, acao, mensagem):
        if acao == "":
            html = paginas.pagina_veiculo(dados, veiculo, mensagem)
        elif acao == "editar":
            html = paginas.pagina_form_veiculo(valores_do_veiculo(veiculo), [], veiculo["id"])
        elif acao == "abastecimentos":
            html = paginas.pagina_abastecimentos(dados, veiculo, mensagem=mensagem)
        elif acao == "manutencoes":
            html = paginas.pagina_manutencoes(dados, veiculo, mensagem=mensagem)
        elif acao == "gastos":
            html = paginas.pagina_gastos(dados, veiculo, mensagem=mensagem)
        else:
            return self.nao_encontrado()
        self.enviar(200, html)

    def post_veiculo(self, dados, veiculo, acao, form):
        acoes = {
            "editar": self.post_editar_veiculo,
            "excluir": self.post_excluir_veiculo,
            "abastecimentos": self.post_abastecimento,
            "manutencoes": self.post_manutencao,
            "gastos": self.post_gasto,
        }
        if acao not in acoes:
            return self.nao_encontrado()
        acoes[acao](dados, veiculo, form)

    # ----- ações (POST) -----
    def post_cadastrar_veiculo(self, dados, form):
        novos, erros = validar_veiculo(dados, form)
        if erros:
            return self.enviar(400, paginas.pagina_form_veiculo(form, erros))
        novos["id"] = gerar_id(dados["veiculos"])
        dados["veiculos"].append(novos)
        self.salvar_e_redirecionar(f"/veiculos/{novos['id']}", "Veículo cadastrado com sucesso!")

    def post_editar_veiculo(self, dados, veiculo, form):
        novos, erros = validar_veiculo(dados, form, ignorar_id=veiculo["id"])
        if erros:
            return self.enviar(400, paginas.pagina_form_veiculo(form, erros, veiculo["id"]))
        veiculo.update(novos)
        self.salvar_e_redirecionar(f"/veiculos/{veiculo['id']}", "Veículo atualizado com sucesso!")

    def post_excluir_veiculo(self, dados, veiculo, form):
        remover_veiculo(dados, veiculo["id"])
        self.salvar_e_redirecionar("/veiculos", "Veículo excluído com sucesso!")

    def post_abastecimento(self, dados, veiculo, form):
        erros = []
        data = val.coletar(erros, val.data(form.get("data"), "Data"))
        km = val.coletar(erros, val.inteiro(form.get("km"), "Quilometragem", 0))
        litros = val.coletar(erros, val.decimal(form.get("litros"), "Litros",
                                                maior_que_zero=True))
        valor = val.coletar(erros, val.decimal(form.get("valor"), "Valor total",
                                               maior_que_zero=True))
        combustivel = val.coletar(erros, val.opcao(form.get("combustivel"), "Combustível",
                                                   COMBUSTIVEIS_ABASTECIMENTO))
        if erros:
            return self.enviar(400, paginas.pagina_abastecimentos(dados, veiculo, form, erros))
        criar_abastecimento(dados, veiculo, data, km, litros, valor, combustivel)
        self.salvar_e_redirecionar(f"/veiculos/{veiculo['id']}/abastecimentos",
                                   "Abastecimento registrado com sucesso!")

    def post_manutencao(self, dados, veiculo, form):
        erros = []
        data = val.coletar(erros, val.data(form.get("data"), "Data"))
        km = val.coletar(erros, val.inteiro(form.get("km"), "Quilometragem", 0))
        tipo = val.coletar(erros, val.opcao(form.get("tipo"), "Tipo", TIPOS_MANUTENCAO))
        descricao = val.coletar(erros, val.texto(form.get("descricao"), "Descrição",
                                                 obrigatorio=(tipo == "Outros")))
        valor = val.coletar(erros, val.decimal(form.get("valor"), "Valor", minimo=0))
        if erros:
            return self.enviar(400, paginas.pagina_manutencoes(dados, veiculo, form, erros))
        criar_manutencao(dados, veiculo, data, km, tipo, descricao, valor)
        self.salvar_e_redirecionar(f"/veiculos/{veiculo['id']}/manutencoes",
                                   "Manutenção registrada com sucesso!")

    def post_gasto(self, dados, veiculo, form):
        erros = []
        data = val.coletar(erros, val.data(form.get("data"), "Data"))
        categoria = val.coletar(erros, val.opcao(form.get("categoria"), "Categoria",
                                                 CATEGORIAS))
        descricao = val.coletar(erros, val.texto(form.get("descricao"), "Descrição"))
        valor = val.coletar(erros, val.decimal(form.get("valor"), "Valor",
                                               maior_que_zero=True))
        if erros:
            return self.enviar(400, paginas.pagina_gastos(dados, veiculo, form, erros))
        criar_gasto(dados, veiculo["id"], data, categoria, descricao, valor)
        self.salvar_e_redirecionar(f"/veiculos/{veiculo['id']}/gastos",
                                   "Gasto registrado com sucesso!")


def criar_servidor():
    """Abre o servidor na primeira porta livre entre 8000 e 8010."""
    for porta in PORTAS:
        try:
            servidor = HTTPServer((HOST, porta), Handler)
        except OSError:
            continue
        servidor.dados = carregar_dados()
        return servidor
    return None


def main():
    servidor = criar_servidor()
    if servidor is None:
        print("Erro: não foi possível abrir uma porta entre 8000 e 8010.")
        return

    url = f"http://{HOST}:{servidor.server_address[1]}"
    print("CarManager (versão web) rodando!")
    print(f"Abra no navegador: {url}")
    print("Para encerrar, aperte Ctrl+C aqui no terminal.\n")
    webbrowser.open(url)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado. Até logo!")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
