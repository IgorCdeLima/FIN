# FIN — Controle Financeiro Pessoal

Aplicativo desktop para registrar entradas e saídas financeiras e acompanhar a evolução do saldo em dashboards por dia, mês e ano. A interface é feita em **HTML/CSS/JavaScript** e roda em uma janela nativa via **pywebview**. Os dados ficam em um banco **SQLite** local, separado por usuário.

> Projeto pessoal, de ideia e autoria própria, criado para ter um lugar onde guardar os próprios dados financeiros e analisá-los depois.

---

## Sumário

- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como executar](#como-executar)
- [Gerar o executável](#gerar-o-executável)
- [Onde os dados ficam salvos](#onde-os-dados-ficam-salvos)
- [Modelo de dados](#modelo-de-dados)
- [Ferramentas de massa de dados](#ferramentas-de-massa-de-dados)
- [Status do projeto](#status-do-projeto)
- [Melhorias futuras](#melhorias-futuras)
- [Autor](#autor)

---

## Funcionalidades

- **Cadastro e login de usuários**: cada usuário tem o próprio banco SQLite. A senha é guardada como hash **PBKDF2-HMAC-SHA256** (100.000 iterações, com salt aleatório) e nunca em texto puro. A comparação do hash é feita em tempo constante (`hmac.compare_digest`).
- **Lançamento de transações**: data, categoria, tipo (entrada ou saída), valor com máscara de moeda (`R$ 1.234,56`) e descrição.
- **Categorias personalizadas**: cadastro de novos nomes de transação (Mercado, Faculdade, Pix...) que aparecem na lista de seleção. Todo usuário novo já começa com a categoria **"Sem categoria"**.
- **Dashboard** com [Apache ECharts](https://echarts.apache.org/):
  - card com o **saldo total** (entradas − saídas), em azul quando positivo e em vermelho quando negativo;
  - **gráfico de pizza** com a proporção entre entradas e saídas do período;
  - **gráfico de evolução** por **dia** (no mês), por **mês** (no ano) ou por **ano** (todo o histórico);
  - seletores de ano e mês preenchidos com os períodos que têm dados, e um botão "hoje" que volta ao mês atual.
- **Consulta mensal**: tabela com todos os lançamentos de um mês.
- **Gerador de dados de teste**: o botão "Adicionar" gera, trata e insere 5.001 lançamentos fictícios de uma vez (veja [Ferramentas de massa de dados](#ferramentas-de-massa-de-dados)).

---

## Arquitetura

```
┌───────────────────────── Janela pywebview ─────────────────────────┐
│                                                                    │
│   web/  (HTML + CSS + JS + ECharts)                                │
│      │                                                             │
│      │  window.pywebview.api.<método>(...)  →  Promise             │
│      ▼                                                             │
│   plugins/controller.py  (Controller: exposto como js_api)         │
│      │                                                             │
│      ▼                                                             │
│   plugins/data_banking/sqlite.py  (DataBankingSQLite)              │
│      │                                                             │
└──────┼─────────────────────────────────────────────────────────────┘
       ▼
  %LOCALAPPDATA%\FIN\
     ├── users.json                 (salt, hash e localização do banco de cada usuário)
     └── data\<token>\<token>.db    (um banco SQLite por usuário)
```

- O **frontend** chama métodos Python diretamente pela ponte do pywebview (`js_api=self`). Cada chamada devolve uma Promise com um dicionário `{ok, msg, ...}`.
- O **Controller** recebe as chamadas da interface, separa a data em ano, mês e dia e delega para a camada de dados.
- A **camada de dados** abre uma conexão SQLite por operação, sempre fechada ao final (`contextlib.closing`), e devolve os resultados já prontos para o JavaScript. Ao fazer login, as tabelas que faltarem são criadas automaticamente, então bancos criados por versões anteriores continuam compatíveis.

---

## Tecnologias

| Ferramenta | Uso |
|---|---|
| Python 3.10+ | Backend (usa `match/case`) |
| [pywebview](https://pywebview.flowrl.com/) | Janela desktop nativa com a interface web |
| SQLite (`sqlite3`, nativo) | Armazenamento local |
| pandas | Leitura e tratamento dos CSVs de massa de dados |
| Apache ECharts 5.6.0 (CDN) | Gráficos do dashboard |
| PyInstaller | Geração do executável (`main.spec`) |
| Fonte Tomorrow (OFL) | Tipografia da interface |

---

## Estrutura do projeto

```
FIN/
├── main.py                      # Ponto de entrada: instancia o Controller e abre a janela
├── main.spec                    # Configuração do PyInstaller (gera dist/FIN.exe)
├── porco.ico                    # Ícone do aplicativo
├── requirements.txt
├── plugins/
│   ├── info.py                  # Caminhos de leitura (web/) e de escrita (%LOCALAPPDATA%\FIN)
│   ├── controller.py            # API exposta ao JavaScript
│   ├── data_banking/
│   │   ├── sqlite.py            # Banco local: usuários, transações, consultas do dashboard
│   │   └── postgresql.py        # Versão inicial com PostgreSQL (não usada atualmente)
│   └── tools/
│       ├── gerador_csv.py       # Gera um CSV "sujo" com 5.001 transações fictícias (botão Adicionar)
│       ├── cleaner_csv.py       # Limpa e padroniza esse CSV (botão Adicionar)
│       └── inserir_csv.py       # Script antigo de carga em massa (legado, não usado pelo app)
├── file_csv/
│   ├── dados_brutos.csv         # Exemplo de saída do gerador (formato sujo)
│   └── dados.csv                # Exemplo de saída do tratamento
└── web/
    ├── menu_login.html          # Tela de login e cadastro
    ├── pages/
    │   ├── menu_principal.html  # Dashboard
    │   ├── insert_data.html     # Lançamento de transações e cadastro de categorias
    │   └── print_table.html     # Consulta mensal
    ├── js/
    │   ├── menu.js              # Login, navegação, inserção, máscara de moeda, tabela
    │   ├── dashboard.js         # Gráficos e seletores do dashboard
    │   └── transactions.js      # Carrega e cadastra categorias
    └── css/                     # Estilos, imagem de fundo e fonte Tomorrow
```

---

## Como executar

### Pré-requisitos

- **Python 3.10 ou superior**
- **Windows 10/11** com o **Microsoft Edge WebView2 Runtime** (já vem instalado nas versões atuais do Windows). O pywebview também roda no Linux e no macOS, mas o projeto foi desenvolvido e testado no Windows.
- **Conexão com a internet** para os gráficos, porque o ECharts é carregado por CDN.

### Passo a passo

```bash
git clone https://github.com/IgorCdeLima/FIN.git
cd FIN
python -m venv venv
```

Ative o ambiente virtual:

```bash
venv\Scripts\activate
```

Instale as dependências e rode:

```bash
pip install -r requirements.txt
python main.py
```

### Primeiro uso

1. Digite um usuário e uma senha e clique em **CADASTRAR**.
2. Com os mesmos dados, clique em **ENTRAR**.
3. Na tela de **Inserir**, cadastre suas categorias em "Cadastre uma Transação" e comece a lançar entradas e saídas.
4. Volte ao dashboard para ver o saldo e os gráficos.

---

## Gerar o executável

Instale o PyInstaller:

```bash
pip install pyinstaller
```

Gere o executável a partir da raiz do projeto:

```bash
pyinstaller main.spec
```

O executável é gerado em `dist/FIN.exe`, em modo janela (sem console) e com o ícone `porco.ico`. Só a pasta `web/` vai embutida nele. Os dados do usuário são criados em `%LOCALAPPDATA%\FIN` no primeiro uso, então não é preciso criar nenhuma pasta antes do build.

---

## Onde os dados ficam salvos

A aplicação separa os arquivos **somente leitura** (a interface, dentro do projeto ou do executável) dos arquivos **graváveis** (os dados do usuário):

| Caminho | Conteúdo |
|---|---|
| `%LOCALAPPDATA%\FIN\users.json` | Para cada usuário: salt, hash da senha, pasta e nome do arquivo do banco |
| `%LOCALAPPDATA%\FIN\data\<token>\<token>.db` | Banco SQLite do usuário. Os nomes da pasta e do arquivo são hashes SHA-256 |
| `%LOCALAPPDATA%\FIN\file_csv\` | CSVs intermediários do gerador de dados de teste (`dados_brutos.csv` e `dados.csv`) |

Para fazer **backup**, copie a pasta `%LOCALAPPDATA%\FIN` inteira. Apagá-la remove todos os usuários e dados.

> O login protege o acesso **pela interface**. Os arquivos `.db` não são criptografados: quem tiver acesso à pasta consegue abri-los com qualquer leitor de SQLite.

---

## Modelo de dados

Cada usuário tem um banco com duas tabelas:

**`transactions`**: os lançamentos

| Coluna | Tipo | Observação |
|---|---|---|
| `id` | INTEGER | PK, autoincremento |
| `year`, `month`, `day` | TEXT | Data guardada em colunas separadas, para facilitar as agregações do dashboard |
| `transition_name` | TEXT | Categoria |
| `entry` | REAL | Valor de entrada (padrão 0) |
| `exit` | REAL | Valor de saída (padrão 0) |
| `description` | TEXT | Opcional |

**`transictions_name`**: as categorias cadastradas (`id`, `transictions` único)

O saldo é sempre calculado como `SUM(entry) − SUM(exit)`. Os valores são arredondados para 2 casas decimais ao serem gravados, e as somas também são arredondadas, o que evita resíduos de ponto flutuante (como `0.1 + 0.2 = 0.30000000000000004`).

Só os tipos `entry` e `exit` são aceitos como coluna de valor. Qualquer outro valor é recusado antes de chegar ao SQL.

---

## Ferramentas de massa de dados

Para testar o dashboard com volume, o botão **"Adicionar"** do dashboard roda um pipeline completo de geração, tratamento e carga de dados fictícios:

```
Adicionar  →  gerador_csv.py  →  dados_brutos.csv  →  cleaner_csv.py  →  dados.csv  →  banco do usuário
               (gera sujo)                             (trata)
```

1. **Geração (`gerador_csv.py`):** cria o `dados_brutos.csv` com 5.001 transações aleatórias entre 2020 e 2025, de propósito "sujas": datas em formatos e separadores variados (`5:5:2024`, `2023;4;17`), valores como `"R$ 1079,35"`, `"R$00,00"` ou vazios, nomes com caixa irregular e campos nulos.
2. **Tratamento (`cleaner_csv.py`):** padroniza tudo em `dados.csv`: datas em `AAAA-MM-DD`, valores numéricos, nomes capitalizados, categoria vazia como "Sem categoria", e uma linha por lançamento com as colunas `value` e `type_value` (`entry`/`exit`).
3. **Carga:** insere o `dados.csv` no banco do usuário logado, numa única transação.

Cada clique gera uma massa **nova e diferente** e a **soma** ao que já existe no banco. Duplicados são aceitos de propósito. O app pede confirmação antes, informa quantos lançamentos entraram e recarrega o dashboard. O processo leva menos de um segundo.

Os CSVs intermediários são gravados em `%LOCALAPPDATA%\FIN\file_csv\` e sobrescritos a cada clique. Os arquivos em `file_csv/` do repositório são um exemplo dessa saída.

> **Use um usuário de teste.** Os dados são inteiramente fictícios e o app ainda não tem como excluir lançamentos. Para desfazer, só apagando o usuário.

---

## Status do projeto

**Versão 1.1.3: funcional e pausado.** O fluxo principal está completo e em uso: cadastro, login, lançamentos, categorias, dashboard e consulta mensal. O executável também foi gerado.

O projeto começou com **PostgreSQL** (`postgresql.py`) e migrou para **SQLite** para virar um aplicativo autocontido, que não depende de servidor de banco.

---

## Autor

**Igor Cechinato de Lima**
GitHub: [@IgorCdeLima](https://github.com/IgorCdeLima)
