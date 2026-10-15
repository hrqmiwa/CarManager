# CarManager

Sistema de gerenciamento de veículos desenvolvido em Python para organizar veículos, abastecimentos, manutenções e gastos. O projeto pode ser utilizado pelo terminal ou por uma interface web local.

## Objetivo

Facilitar o controle das informações e despesas de veículos em um só lugar, mantendo os registros salvos localmente em um arquivo JSON.

## Funcionalidades

- Cadastrar, listar, consultar, editar e excluir veículos.
- Registrar abastecimentos com data, quilometragem, litros, combustível e valor.
- Calcular o preço por litro e estimar o consumo médio em km/l.
- Registrar manutenções e consultar o histórico.
- Registrar gastos e consultar totais por veículo e categoria.
- Exibir um resumo dos gastos e registros de cada veículo.
- Validar entradas e apresentar mensagens para dados inválidos.
- Utilizar uma interface web responsiva ou o menu pelo terminal.
- Salvar os dados em JSON para que permaneçam disponíveis entre execuções.

## Tecnologias utilizadas

- Python 3.8 ou superior.
- Bibliotecas padrão do Python: `json`, `pathlib`, `datetime`, `re`, `math`, `http.server`, `html`, `urllib`, `webbrowser` e `unittest`.
- HTML, CSS e JavaScript para a interface web.
- Arquivo JSON para persistência local dos dados.
- Git e GitHub para versionamento e entrega do projeto.

O projeto não utiliza bibliotecas externas; por isso, não é necessário instalar pacotes adicionais. O arquivo `requirements.txt` está incluído para documentar essa informação.

## Estrutura do projeto

```text
CarManager/
├── src/
│   ├── main.py              # ponto de entrada da versão de terminal
│   ├── web.py               # servidor e rotas da versão web
│   ├── paginas.py           # construção das páginas HTML
│   ├── web_validacao.py     # validação dos formulários web
│   ├── static/
│   │   ├── app.js           # interações da interface
│   │   └── style.css        # estilos e responsividade
│   ├── storage.py           # leitura e gravação dos dados
│   ├── utils.py             # validações e formatação
│   ├── veiculos.py          # operações com veículos
│   ├── abastecimentos.py    # abastecimentos e consumo médio
│   ├── manutencoes.py       # registros de manutenção
│   ├── gastos.py            # registros e totais de gastos
│   └── resumo.py            # resumo por veículo
├── tests/
│   ├── test_funcoes.py      # testes da lógica do sistema
│   └── test_web.py          # testes de validação web
├── docs/
│   └── relatorio.md         # documentação complementar
├── imagens/                 # local para capturas de tela do sistema
├── .gitignore
├── README.md
└── requirements.txt
```

## Requisitos

- Python 3.8 ou superior.
- Git, caso deseje clonar e enviar o projeto ao GitHub.

## Como executar

### 1. Baixar o projeto

Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/SEU-USUARIO/CarManager.git
cd CarManager
```

Se o projeto já estiver no computador, abra o terminal na pasta raiz `CarManager`.

### 2. Executar a versão web

```bash
python src/web.py
```

Abra no navegador o endereço informado no terminal (normalmente `http://127.0.0.1:8000`). Para encerrar o servidor, volte ao terminal e pressione `Ctrl+C`.

### 3. Executar a versão de terminal

Em outro momento, ou após encerrar a versão web, execute:

```bash
python src/main.py
```

No Windows, se o comando `python` não funcionar, tente `py`. No Linux ou macOS, pode ser necessário usar `python3`.

### 4. Executar os testes

Na pasta raiz do projeto, execute:

```bash
python -m unittest discover -s tests -v
```

Os testes verificam funções de validação, cálculos e regras principais do sistema.

## Armazenamento dos dados

Na primeira execução, o sistema cria a pasta `data/` e o arquivo JSON de dados conforme necessário. Essa pasta está no `.gitignore` para evitar publicar dados locais. Para a entrega, não inclua dados reais ou pessoais; use apenas exemplos fictícios.

Cada abastecimento e manutenção também registra um gasto na categoria correspondente. Portanto, não é necessário lançar novamente o mesmo valor na tela de gastos. O consumo médio é uma estimativa e considera que o tanque é completado em cada abastecimento.

## Integrantes

- Henrique Miwa da Silva
- Mateus Silva Dalmarco

**Turma/curso:** 2º DS — ETEC

## Observações e limitações

- Os dados ficam armazenados localmente no arquivo JSON; não há banco de dados remoto ou sincronização entre computadores.
- A versão web padrão é um servidor local para uso no próprio computador, não uma hospedagem pública.
- Utilize dados fictícios para testes e demonstrações. Não cadastre placas reais nem informações pessoais.
- O projeto é educacional e pode receber melhorias futuras, como exportação de relatórios e cópias de segurança dos dados.
