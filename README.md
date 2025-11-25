# Calmou - Backend com MongoDB

Este é o backend do projeto "Calmou", um sistema de bem-estar e saúde mental. O projeto é construído em Python e utiliza o MongoDB como banco de dados. Ele é composto por uma API RESTful desenvolvida com Flask (destinada a calmou) e um conjunto de scripts para administração ou outras tarefas.

## Visão Geral da Arquitetura
## Markdown ##
<img width="1785" height="1105" alt="diagrama_relacional" src="https://github.com/user-attachments/assets/47eb2fb3-3109-4786-b622-4c99f013aa8d" />
## Markdown ##

O projeto está dividido em tres partes principais:

1.  **Aplicação Mobile (IOS/ANDROID) (`../`)**: Aplicacao mobile desenvolvida com react native.
2.  **Aplicação Terminal Principal/Scripts (`/`)**: Contém scripts e a lógica principal da aplicação, com suas próprias dependências.
3.  **API Flask (`/api`)**: Uma API RESTful para servir dados a um cliente, como um aplicativo móvel React Native.

O banco de dados MongoDB é modelado em 7 coleções principais, conforme descrito no arquivo `diagrama_relacional.sql`: `usuarios`, `meditacoes`, `classificacoes_humor`, `historico_meditacoes`, `questionarios`, `avaliacoes` e `notificacoes`.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

- **Python 3.8 ou superior**
- **MongoDB 4.4 ou superior** (pode ser uma instância local ou uma conta no MongoDB Atlas)
- **pip** (gerenciador de pacotes do Python)

## Configuração do Ambiente

O projeto utiliza variáveis de ambiente para gerenciar configurações sensíveis, como as credenciais do banco de dados. Você precisará criar um arquivo `.env` em cada um dos diretórios (`/` e `/api`).

### 1. Arquivo `.env` para a Aplicação Principal

Crie um arquivo chamado `.env` na raiz do projeto (`mongo/`) com o seguinte conteúdo:

```env
# String de conexão do MongoDB (local ou Atlas)
# Exemplo Atlas: MONGODB_URI="mongodb+srv://<user>:<password>@<cluster-url>/calmou?retryWrites=true&w=majority"
# Exemplo Local: MONGODB_URI="mongodb://localhost:27017/calmou"
MONGODB_URI="sua_string_de_conexao_aqui"
```

### 2. Arquivo `.env` para a API Flask

Crie um arquivo chamado `.env` dentro do diretório `api/` (`mongo/api/`) com o seguinte conteúdo:

```env
# String de conexão do MongoDB (pode ser a mesma do passo anterior)
MONGODB_URI="sua_string_de_conexao_aqui"

# Chave secreta para assinar os tokens JWT (JSON Web Tokens)
# Gere uma chave segura, por exemplo, usando: python -c 'import secrets; print(secrets.token_hex(32))'
JWT_SECRET_KEY="sua_chave_secreta_jwt_aqui"

# Ambiente do Flask (development ou production)
FLASK_ENV="development"
```

## Instalação e Execução

Siga os passos abaixo para cada parte do projeto. Recomenda-se o uso de ambientes virtuais (`venv`) separados para evitar conflitos de dependência.

### Parte 1: Aplicação Principal / Scripts

Estes passos são para executar o script `principal.py` (se aplicável).

```bash
# 1. Navegue até a raiz do projeto
cd /caminho/para/o/projeto/mongo

# 2. Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate
# No Windows, use: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o script principal (exemplo)
python principal.py
```

### Parte 2: API Flask

Estes passos são para executar o servidor da API.

```bash
# 1. Navegue até o diretório da API
cd /caminho/para/o/projeto/mongo/api

# 2. Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate
# No Windows, use: .venv\Scripts\activate

# 3. Instale as dependências da API
pip install -r requirements.txt

# 4. Execute o servidor de desenvolvimento Flask
flask run

# O servidor estará rodando em http://127.0.0.1:5000
```

### Executando a API em Produção (com Gunicorn)

Para um ambiente de produção, o `gunicorn` já está listado nas dependências. Supondo que sua instância Flask se chame `app` dentro de um arquivo `app.py` ou similar:

```bash
# A partir do diretório /api
# gunicorn --bind 0.0.0.0:8000 nome_do_arquivo:nome_da_instancia_flask
gunicorn --bind 0.0.0.0:8000 app:app
```

## Dependências do Projeto

- **Flask**: Micro-framework web para a criação da API.
- **PyMongo**: Driver oficial do Python para interagir com o MongoDB.
- **Flask-JWT-Extended**: Para gerenciamento de autenticação via JSON Web Tokens.
- **Bcrypt**: Para hashing seguro de senhas.
- **Marshmallow**: Para validação e serialização de dados (esquemas).
- **Gunicorn**: Servidor WSGI para rodar a aplicação em produção.
- **python-dotenv**: Para carregar variáveis de ambiente a partir de arquivos `.env`.

## Colaboradores
- **Derek Cobain**
- **Dyone Andrade**

## Mestre / Mentor

- **Howard Roatti**
