


Integrantes

Nome: Henrique Miwa da Silva
Nome: Mateus Silva Dalmarco


1. Introdução e objetivo

O CarManager é um sistema desenvolvido em Python para organizar informações relacionadas a veículos em um único lugar. Seu objetivo é facilitar o acompanhamento dos dados dos veículos e o controle de despesas, permitindo registrar abastecimentos, manutenções e outros gastos. Os dados são armazenados localmente em arquivo JSON, para que possam ser carregados novamente quando o programa for executado.

2. Funcionalidades

Cadastrar, listar, consultar, editar e excluir veículos.

Registrar abastecimentos, incluindo data, quilometragem, combustível, quantidade de litros e valor.

Consultar o histórico de abastecimentos e estimar o consumo médio em quilômetros por litro quando há dados suficientes.

Registrar manutenções e consultar o histórico de serviços.

Registrar gastos e consultar os valores totais por veículo e categoria.

Exibir um resumo do veículo com quilometragem, gastos, quantidade de registros, consumo médio estimado e última manutenção.

Validar entradas e apresentar mensagens quando os dados informados forem inválidos.

Utilizar o sistema pelo menu do terminal ou pela interface web local.

3. Como o sistema foi organizado

O código foi dividido em módulos para separar responsabilidades e facilitar a leitura, a manutenção e a realização de testes.

main.py: apresenta o menu do terminal e encaminha cada opção para a função correspondente.

web.py: inicia o servidor web local e trata as rotas e requisições da interface.

paginas.py: monta o conteúdo HTML das páginas exibidas no navegador.

web_validacao.py: valida os dados enviados pelos formulários da interface web.

storage.py: carrega e salva os dados do sistema em formato JSON.

utils.py: reúne funções auxiliares de validação, formatação e exibição.

veiculos.py: contém as operações de cadastro, consulta, edição, listagem e exclusão de veículos.

abastecimentos.py: registra abastecimentos, consulta o histórico e calcula o consumo médio.

manutencoes.py: registra manutenções e consulta os serviços realizados.

gastos.py: registra despesas e calcula totais por veículo e categoria.

resumo.py: reúne informações do veículo para apresentar um resumo.

static/app.js: implementa pequenas interações da interface web.

static/style.css: define a aparência e a adaptação visual da interface a diferentes tamanhos de tela.

A pasta tests/ contém os testes automatizados. O arquivo test_funcoes.py verifica funções e cálculos do sistema, enquanto test_web.py verifica validações e regras relacionadas à interface web. A pasta docs/ guarda a documentação do projeto, e a pasta imagens/ pode armazenar capturas de tela que demonstrem seu funcionamento.

A divisão em arquivos torna o código mais organizado e facilita a identificação e a correção de possíveis erros.

4. Dificuldades encontradas

Uma das dificuldades foi organizar as diferentes funcionalidades sem concentrar todo o código em um único arquivo. A divisão por módulos ajudou a separar o cadastro de veículos, os abastecimentos, as manutenções, os gastos e os resumos.

Também foi necessário validar as informações digitadas pelo usuário e manter os registros relacionados coerentes, como associar despesas a abastecimentos e manutenções. As funções auxiliares e os testes automatizados ajudam a verificar esses comportamentos e a identificar problemas com mais facilidade.

5. Testes realizados

Foram executados testes automatizados utilizando o comando:

python -m unittest discover -s tests -v

O resultado registrado foi de 24 testes aprovados sem erros. Os testes verificam formatação, geração de identificadores, validação de placas e campos, cálculo de consumo médio, totais de gastos, histórico de manutenções, atualização da quilometragem, associação de gastos a abastecimentos e manutenções, exclusão de registros relacionados e tratamento de conteúdo HTML.

Para os testes manuais, o sistema pode ser iniciado pelo comando python src/main.py, para utilizar o menu do terminal, ou por python src/web.py, para abrir a interface web local.

As verificações manuais devem incluir o cadastro e a consulta de um veículo, o registro de um abastecimento e de uma manutenção, a conferência dos gastos e do resumo e o teste de informações inválidas. Esses procedimentos devem ser conferidos no computador antes da entrega final.

6. Conclusão

O desenvolvimento do CarManager permitiu praticar conceitos de programação em Python, organização de código em módulos, validação de dados, armazenamento em JSON, construção de uma interface web e realização de testes automatizados.

O sistema reúne informações que ajudam a acompanhar veículos e suas despesas, facilitando a organização dos registros. Como melhorias futuras, seria possível implementar a exportação de relatórios, cópias de segurança, filtros mais avançados e integração com um banco de dados, além de preparar uma versão para hospedagem pública.

Observações

Antes da entrega, é necessário preencher o nome completo da ETEC e o RM do integrante. Recomenda-se utilizar dados fictícios nos testes e não publicar informações pessoais ou registros reais.