-- =======================================================
-- SISTEMA CALMOU - MODELO RELACIONAL
-- Conversão do modelo MongoDB para SQL
-- =======================================================

-- ===========================
-- TABELA: usuarios
-- ===========================
CREATE TABLE usuarios (
    _id VARCHAR(24) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    data_nascimento DATE,
    tipo_sanguineo VARCHAR(3),
    alergias TEXT,
    foto_perfil VARCHAR(255),
    data_cadastro DATETIME NOT NULL,
    endereco_json TEXT,
    config_json TEXT
);

-- ===========================
-- TABELA: meditacoes
-- ===========================
CREATE TABLE meditacoes (
    _id VARCHAR(24) PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    duracao_minutos INT NOT NULL,
    url_audio VARCHAR(255),
    tipo VARCHAR(50) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    imagem_capa VARCHAR(255),
    ativa BOOLEAN DEFAULT TRUE,
    data_criacao DATETIME
);

-- ===========================
-- TABELA: classificacoes_humor
-- ===========================
CREATE TABLE classificacoes_humor (
    _id VARCHAR(24) PRIMARY KEY,
    usuario_id VARCHAR(24) NOT NULL,
    nivel_humor INT NOT NULL,
    sentimento_principal VARCHAR(50) NOT NULL,
    notas TEXT,
    data_classificacao DATETIME NOT NULL,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(_id)
);

-- ===========================
-- TABELA: historico_meditacoes
-- ===========================
CREATE TABLE historico_meditacoes (
    _id VARCHAR(24) PRIMARY KEY,
    usuario_id VARCHAR(24) NOT NULL,
    meditacao_id VARCHAR(24) NOT NULL,
    data_conclusao DATETIME NOT NULL,
    duracao_real_minutos INT,
    concluiu BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(_id),
    FOREIGN KEY (meditacao_id) REFERENCES meditacoes(_id)
);

-- ===========================
-- TABELA: questionarios
-- ===========================
CREATE TABLE questionarios (
    _id VARCHAR(24) PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL UNIQUE,
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT,
    versao VARCHAR(10),
    ativo BOOLEAN DEFAULT TRUE,
    perguntas_json TEXT,
    interpretacao_json TEXT
);

-- ===========================
-- TABELA: avaliacoes
-- ===========================
CREATE TABLE avaliacoes (
    _id VARCHAR(24) PRIMARY KEY,
    usuario_id VARCHAR(24) NOT NULL,
    questionario_tipo VARCHAR(20) NOT NULL,
    respostas_json TEXT,
    resultado_score INT NOT NULL,
    resultado_texto TEXT,
    data_avaliacao DATETIME NOT NULL,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(_id),
    FOREIGN KEY (questionario_tipo) REFERENCES questionarios(tipo)
);

-- ===========================
-- TABELA: notificacoes
-- ===========================
CREATE TABLE notificacoes (
    _id VARCHAR(24) PRIMARY KEY,
    usuario_id VARCHAR(24) NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    mensagem TEXT NOT NULL,
    tipo VARCHAR(20),
    data_envio DATETIME NOT NULL,
    lida BOOLEAN DEFAULT FALSE,
    data_leitura DATETIME,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(_id)
);
