"""
Script de Criação COMPLETO de Coleções MongoDB - Calmou API
Cria TODAS as 7 coleções necessárias para o app funcionar 100%
"""

import sys
import os

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conexion.mongo_conexao import MongoDBConnection
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid

def criar_colecoes_completas():
    """Cria TODAS as 7 coleções no MongoDB com validação de schema"""

    print("\n" + "="*70)
    print("CRIAÇÃO COMPLETA DE COLEÇÕES MONGODB - CALMOU API")
    print("7 Coleções para App 100% Funcional")
    print("="*70 + "\n")

    try:
        # Conecta ao MongoDB
        conexao = MongoDBConnection()
        db = conexao.get_database()

        # ==================== COLEÇÃO 1: USUARIOS ====================
        print("📦 Criando coleção 'usuarios'...")

        usuarios_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["nome", "email", "password_hash", "data_cadastro"],
                "properties": {
                    "nome": {"bsonType": "string"},
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                    },
                    "password_hash": {"bsonType": "string"},
                    "cpf": {"bsonType": ["string", "null"]},
                    "data_nascimento": {"bsonType": ["date", "null"]},
                    "tipo_sanguineo": {"bsonType": ["string", "null"]},
                    "alergias": {"bsonType": ["string", "null"]},
                    "foto_perfil": {"bsonType": ["string", "null"]},
                    "data_cadastro": {"bsonType": "date"},
                    "endereco": {"bsonType": ["object", "null"]},
                    "config": {"bsonType": ["object", "null"]}
                }
            }
        }

        try:
            db.create_collection("usuarios", validator=usuarios_validator)
            print("  ✅ Coleção 'usuarios' criada")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'usuarios' já existe")

        usuarios_collection = db["usuarios"]
        usuarios_collection.create_index([("email", ASCENDING)], unique=True, name="idx_email_unique")
        usuarios_collection.create_index([("cpf", ASCENDING)], unique=True, sparse=True, name="idx_cpf_unique")
        usuarios_collection.create_index([("data_cadastro", DESCENDING)], name="idx_data_cadastro")
        print("  ✅ Índices criados: email (unique), cpf (unique), data_cadastro")

        # ==================== COLEÇÃO 2: MEDITACOES ====================
        print("\n📦 Criando coleção 'meditacoes'...")

        meditacoes_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["titulo", "descricao", "duracao_minutos", "tipo", "categoria"],
                "properties": {
                    "titulo": {"bsonType": "string"},
                    "descricao": {"bsonType": "string"},
                    "duracao_minutos": {"bsonType": "int", "minimum": 1},
                    "url_audio": {"bsonType": ["string", "null"]},
                    "tipo": {"bsonType": "string"},
                    "categoria": {"bsonType": "string"},
                    "imagem_capa": {"bsonType": ["string", "null"]},
                    "ativa": {"bsonType": "bool"},
                    "data_criacao": {"bsonType": "date"}
                }
            }
        }

        try:
            db.create_collection("meditacoes", validator=meditacoes_validator)
            print("  ✅ Coleção 'meditacoes' criada")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'meditacoes' já existe")

        meditacoes_collection = db["meditacoes"]
        meditacoes_collection.create_index([("categoria", ASCENDING)], name="idx_categoria")
        meditacoes_collection.create_index([("tipo", ASCENDING)], name="idx_tipo")
        meditacoes_collection.create_index([("categoria", ASCENDING), ("duracao_minutos", ASCENDING)], name="idx_categoria_duracao")
        meditacoes_collection.create_index([("titulo", "text"), ("descricao", "text")], name="idx_text_search")
        print("  ✅ Índices criados: categoria, tipo, categoria+duracao, text_search")

        # ==================== COLEÇÃO 3: CLASSIFICACOES_HUMOR ====================
        print("\n📦 Criando coleção 'classificacoes_humor'...")

        humor_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usuario_id", "nivel_humor", "sentimento_principal", "data_classificacao"],
                "properties": {
                    "usuario_id": {"bsonType": "objectId"},
                    "nivel_humor": {"bsonType": "int", "minimum": 1, "maximum": 5},
                    "sentimento_principal": {"bsonType": "string"},
                    "notas": {"bsonType": ["string", "null"]},
                    "data_classificacao": {"bsonType": "date"}
                }
            }
        }

        try:
            db.create_collection("classificacoes_humor", validator=humor_validator)
            print("  ✅ Coleção 'classificacoes_humor' criada")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'classificacoes_humor' já existe")

        humor_collection = db["classificacoes_humor"]
        humor_collection.create_index([("usuario_id", ASCENDING)], name="idx_usuario")
        humor_collection.create_index([("data_classificacao", DESCENDING)], name="idx_data")
        humor_collection.create_index([("usuario_id", ASCENDING), ("data_classificacao", DESCENDING)], name="idx_usuario_data")
        print("  ✅ Índices criados: usuario_id, data_classificacao, usuario_id+data")

        # ==================== COLEÇÃO 4: HISTORICO_MEDITACOES ====================
        print("\n📦 Criando coleção 'historico_meditacoes'...")

        historico_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usuario_id", "meditacao_id", "data_conclusao"],
                "properties": {
                    "usuario_id": {"bsonType": "objectId"},
                    "meditacao_id": {"bsonType": "objectId"},
                    "data_conclusao": {"bsonType": "date"},
                    "duracao_real_minutos": {"bsonType": ["int", "null"]},
                    "concluiu": {"bsonType": "bool"}
                }
            }
        }

        try:
            db.create_collection("historico_meditacoes", validator=historico_validator)
            print("  ✅ Coleção 'historico_meditacoes' criada")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'historico_meditacoes' já existe")

        historico_collection = db["historico_meditacoes"]
        historico_collection.create_index([("usuario_id", ASCENDING)], name="idx_usuario")
        historico_collection.create_index([("meditacao_id", ASCENDING)], name="idx_meditacao")
        historico_collection.create_index([("data_conclusao", DESCENDING)], name="idx_data")
        historico_collection.create_index([("usuario_id", ASCENDING), ("data_conclusao", DESCENDING)], name="idx_usuario_data")
        print("  ✅ Índices criados: usuario_id, meditacao_id, data_conclusao, usuario_id+data")

        # ==================== COLEÇÃO 5: AVALIACOES ====================
        print("\n📦 Criando coleção 'avaliacoes'...")

        avaliacoes_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usuario_id", "tipo", "resultado_score", "data_avaliacao"],
                "properties": {
                    "usuario_id": {"bsonType": "objectId"},
                    "tipo": {
                        "bsonType": "string",
                        "enum": ["ansiedade", "depressao", "estresse", "burnout"]
                    },
                    "respostas": {"bsonType": ["object", "null"]},
                    "resultado_score": {"bsonType": "int"},
                    "resultado_texto": {"bsonType": ["string", "null"]},
                    "data_avaliacao": {"bsonType": "date"}
                }
            }
        }

        try:
            db.create_collection("avaliacoes", validator=avaliacoes_validator)
            print("  ✅ Coleção 'avaliacoes' criada")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'avaliacoes' já existe")

        avaliacoes_collection = db["avaliacoes"]
        avaliacoes_collection.create_index([("usuario_id", ASCENDING)], name="idx_usuario")
        avaliacoes_collection.create_index([("tipo", ASCENDING)], name="idx_tipo")
        avaliacoes_collection.create_index([("data_avaliacao", DESCENDING)], name="idx_data")
        avaliacoes_collection.create_index([("usuario_id", ASCENDING), ("tipo", ASCENDING)], name="idx_usuario_tipo")
        print("  ✅ Índices criados: usuario_id, tipo, data_avaliacao, usuario_id+tipo")

        # ==================== COLEÇÃO 6: NOTIFICACOES ====================
        print("\n📦 Criando coleção 'notificacoes'...")

        notificacoes_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usuario_id", "titulo", "mensagem", "data_envio"],
                "properties": {
                    "usuario_id": {"bsonType": "objectId"},
                    "titulo": {"bsonType": "string"},
                    "mensagem": {"bsonType": "string"},
                    "tipo": {"bsonType": ["string", "null"], "enum": [None, "info", "alerta", "sucesso", "lembrete"]},
                    "data_envio": {"bsonType": "date"},
                    "lida": {"bsonType": "bool"},
                    "data_leitura": {"bsonType": ["date", "null"]}
                }
            }
        }

        try:
            db.create_collection("notificacoes", validator=notificacoes_validator)
            print("  ✅ Coleção 'notificacoes' criada")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'notificacoes' já existe")

        notificacoes_collection = db["notificacoes"]
        notificacoes_collection.create_index([("usuario_id", ASCENDING)], name="idx_usuario")
        notificacoes_collection.create_index([("lida", ASCENDING)], name="idx_lida")
        notificacoes_collection.create_index([("data_envio", DESCENDING)], name="idx_data_envio")
        notificacoes_collection.create_index([("usuario_id", ASCENDING), ("lida", ASCENDING)], name="idx_usuario_lida")
        print("  ✅ Índices criados: usuario_id, lida, data_envio, usuario_id+lida")

        # ==================== COLEÇÃO 7: QUESTIONARIOS ====================
        print("\n📦 Criando coleção 'questionarios'...")

        questionarios_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["tipo", "titulo"],
                "properties": {
                    "tipo": {
                        "bsonType": "string",
                        "enum": ["ansiedade", "depressao", "estresse", "burnout"]
                    },
                    "titulo": {"bsonType": "string"},
                    "descricao": {"bsonType": ["string", "null"]},
                    "versao": {"bsonType": ["string", "null"]},
                    "ativo": {"bsonType": "bool"},
                    "perguntas": {"bsonType": ["array", "null"]},
                    "interpretacao": {"bsonType": ["array", "null"]}
                }
            }
        }

        try:
            db.create_collection("questionarios", validator=questionarios_validator)
            print("  ✅ Coleção 'questionarios' criada")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'questionarios' já existe")

        questionarios_collection = db["questionarios"]
        questionarios_collection.create_index([("tipo", ASCENDING)], unique=True, name="idx_tipo_unique")
        questionarios_collection.create_index([("ativo", ASCENDING)], name="idx_ativo")
        print("  ✅ Índices criados: tipo (unique), ativo")

        # ==================== RESUMO ====================
        print("\n" + "="*70)
        print("RESUMO DA CRIAÇÃO")
        print("="*70)

        colecoes = conexao.listar_colecoes()
        print(f"\n📚 Total de coleções: {len(colecoes)}")
        for col in sorted(colecoes):
            count = conexao.contar_documentos(col)
            print(f"  - {col:<30} {count:>5} documentos")

        print("\n✅ TODAS as 7 coleções criadas com sucesso!")
        print("\n📊 Modelagem Completa:")
        print("  1. usuarios              - Dados principais dos usuários")
        print("  2. meditacoes            - Catálogo de meditações")
        print("  3. classificacoes_humor  - Registro de humor")
        print("  4. historico_meditacoes  - Log de meditações realizadas")
        print("  5. avaliacoes            - Resultados de questionários")
        print("  6. notificacoes          - Sistema de notificações")
        print("  7. questionarios         - Templates de avaliações")

        print("\n💡 Próximos passos:")
        print("  1. Insira dados de teste")
        print("  2. Teste os relacionamentos")
        print("  3. Crie os relatórios com as novas coleções")
        print("  4. Atualize a API para usar as coleções separadas\n")

    except Exception as e:
        print(f"\n❌ Erro ao criar coleções: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Fecha conexão
        conexao.fechar_conexao()

if __name__ == "__main__":
    criar_colecoes_completas()
