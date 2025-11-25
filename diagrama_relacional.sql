// ==========================================
// SISTEMA CALMOU - MODELAGEM COMPLETA
// MongoDB convertido para Modelo Relacional
// 7 Coleções - App 100% Funcional
// ==========================================

Table usuarios {
  _id varchar(24) [pk, note: 'ObjectId']
  nome varchar(100) [not null]
  email varchar(100) [not null, unique]
  password_hash varchar(255) [not null]
  cpf varchar(14) [unique]
  data_nascimento date
  tipo_sanguineo varchar(3)
  alergias text
  foto_perfil varchar(255)
  data_cadastro datetime [not null]
  endereco_json text [note: 'JSON: endereço completo']
  config_json text [note: 'JSON: configurações']

  Note: 'Usuários do sistema'
}

Table meditacoes {
  _id varchar(24) [pk]
  titulo varchar(100) [not null]
  descricao text [not null]
  duracao_minutos int [not null]
  url_audio varchar(255)
  tipo varchar(50) [not null]
  categoria varchar(50) [not null]
  imagem_capa varchar(255)
  ativa boolean [default: true]
  data_criacao datetime

  Note: 'Catálogo de meditações'
}

Table classificacoes_humor {
  _id varchar(24) [pk]
  usuario_id varchar(24) [not null, ref: > usuarios._id]
  nivel_humor int [not null, note: '1-5']
  sentimento_principal varchar(50) [not null]
  notas text
  data_classificacao datetime [not null]

  Note: 'Registro diário de humor'
}

Table historico_meditacoes {
  _id varchar(24) [pk]
  usuario_id varchar(24) [not null, ref: > usuarios._id]
  meditacao_id varchar(24) [not null, ref: > meditacoes._id]
  data_conclusao datetime [not null]
  duracao_real_minutos int
  concluiu boolean [default: true]

  Note: 'Log de meditações realizadas (N:N)'
}

Table questionarios {
  _id varchar(24) [pk]
  tipo varchar(20) [not null, unique]
  titulo varchar(100) [not null]
  descricao text
  versao varchar(10)
  ativo boolean [default: true]
  perguntas_json text [note: 'Array de perguntas']
  interpretacao_json text [note: 'Faixas de interpretação']

  Note: 'Templates de questionários'
}

Table avaliacoes {
  _id varchar(24) [pk]
  usuario_id varchar(24) [not null, ref: > usuarios._id]
  questionario_tipo varchar(20) [not null, ref: > questionarios.tipo]
  respostas_json text
  resultado_score int [not null]
  resultado_texto text
  data_avaliacao datetime [not null]

  Note: 'Resultados de questionários psicológicos'
}

Table notificacoes {
  _id varchar(24) [pk]
  usuario_id varchar(24) [not null, ref: > usuarios._id]
  titulo varchar(100) [not null]
  mensagem text [not null]
  tipo varchar(20) [note: 'info|alerta|sucesso|lembrete']
  data_envio datetime [not null]
  lida boolean [default: false]
  data_leitura datetime

  Note: 'Sistema de notificações'
}
