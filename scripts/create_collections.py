"""
Script de Criação de Coleções MongoDB - Calmou API
Cria as coleções necessárias e seus índices
"""

import sys
import os

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conexion.mongo_conexao import MongoDBConnection
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid

def criar_colecoes():
    """Cria as coleções no MongoDB com validação de schema"""

    print("\n" + "="*60)
    print("CRIAÇÃO DE COLEÇÕES MONGODB - CALMOU API")
    print("="*60 + "\n")

    try:
        # Conecta ao MongoDB
        conexao = MongoDBConnection()
        db = conexao.get_database()

        # ==================== COLEÇÃO: USUARIOS ====================
        print("📦 Criando coleção 'usuarios'...")

        # Schema de validação para usuários
        usuarios_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["nome", "email", "password_hash", "data_cadastro"],
                "properties": {
                    "nome": {
                        "bsonType": "string",
                        "description": "Nome do usuário é obrigatório"
                    },
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                        "description": "Email válido é obrigatório"
                    },
                    "password_hash": {
                        "bsonType": "string",
                        "description": "Hash da senha é obrigatório"
                    },
                    "cpf": {
                        "bsonType": ["string", "null"],
                        "description": "CPF do usuário"
                    },
                    "data_nascimento": {
                        "bsonType": ["date", "null"],
                        "description": "Data de nascimento"
                    },
                    "tipo_sanguineo": {
                        "bsonType": ["string", "null"],
                        "description": "Tipo sanguíneo"
                    },
                    "config": {
                        "bsonType": "object",
                        "description": "Configurações do usuário"
                    },
                    "data_cadastro": {
                        "bsonType": "date",
                        "description": "Data de cadastro é obrigatória"
                    },
                    "endereco": {
                        "bsonType": ["object", "null"],
                        "properties": {
                            "pais": {"bsonType": "string"},
                            "estado": {"bsonType": "string"},
                            "cidade": {"bsonType": "string"},
                            "rua": {"bsonType": "string"},
                            "numero": {"bsonType": "string"},
                            "cep": {"bsonType": ["string", "null"]}
                        }
                    },
                    "classificacoes_humor": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["nivel_humor", "sentimento_principal", "data_classificacao"],
                            "properties": {
                                "nivel_humor": {"bsonType": "int", "minimum": 1, "maximum": 5},
                                "sentimento_principal": {"bsonType": "string"},
                                "notas": {"bsonType": ["string", "null"]},
                                "data_classificacao": {"bsonType": "date"}
                            }
                        }
                    },
                    "historico_meditacoes": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["meditacao_id", "data_conclusao"],
                            "properties": {
                                "meditacao_id": {"bsonType": "objectId"},
                                "data_conclusao": {"bsonType": "date"},
                                "duracao_real_minutos": {"bsonType": ["int", "null"]}
                            }
                        }
                    },
                    "resultados_avaliacoes": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["tipo", "resultado_score", "data_avaliacao"],
                            "properties": {
                                "tipo": {
                                    "bsonType": "string",
                                    "enum": ["ansiedade", "depressao", "estresse", "burnout"]
                                },
                                "respostas": {"bsonType": "object"},
                                "resultado_score": {"bsonType": "int"},
                                "resultado_texto": {"bsonType": "string"},
                                "data_avaliacao": {"bsonType": "date"}
                            }
                        }
                    },
                    "notificacoes": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["titulo", "mensagem", "data_envio"],
                            "properties": {
                                "titulo": {"bsonType": "string"},
                                "mensagem": {"bsonType": "string"},
                                "data_envio": {"bsonType": "date"},
                                "lida": {"bsonType": "bool"}
                            }
                        }
                    }
                }
            }
        }

        try:
            db.create_collection("usuarios", validator=usuarios_validator)
            print("  ✅ Coleção 'usuarios' criada com validação de schema")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'usuarios' já existe")

        # Criar índices para usuarios
        usuarios_collection = db["usuarios"]

        # Índice único em email
        usuarios_collection.create_index([("email", ASCENDING)], unique=True, name="idx_email_unique")
        print("  ✅ Índice único criado em 'email'")

        # Índice único em CPF (sparse para permitir nulos)
        usuarios_collection.create_index([("cpf", ASCENDING)], unique=True, sparse=True, name="idx_cpf_unique")
        print("  ✅ Índice único (sparse) criado em 'cpf'")

        # Índice em data_cadastro para ordenação
        usuarios_collection.create_index([("data_cadastro", DESCENDING)], name="idx_data_cadastro")
        print("  ✅ Índice criado em 'data_cadastro'")

        # Índice em classificacoes_humor.data_classificacao
        usuarios_collection.create_index(
            [("classificacoes_humor.data_classificacao", DESCENDING)],
            name="idx_humor_data"
        )
        print("  ✅ Índice criado em 'classificacoes_humor.data_classificacao'")

        # ==================== COLEÇÃO: MEDITACOES ====================
        print("\n📦 Criando coleção 'meditacoes'...")

        # Schema de validação para meditações
        meditacoes_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["titulo", "descricao", "duracao_minutos", "tipo", "categoria"],
                "properties": {
                    "titulo": {
                        "bsonType": "string",
                        "description": "Título da meditação é obrigatório"
                    },
                    "descricao": {
                        "bsonType": "string",
                        "description": "Descrição é obrigatória"
                    },
                    "duracao_minutos": {
                        "bsonType": "int",
                        "minimum": 1,
                        "description": "Duração em minutos é obrigatória"
                    },
                    "url_audio": {
                        "bsonType": ["string", "null"],
                        "description": "URL do áudio"
                    },
                    "tipo": {
                        "bsonType": "string",
                        "description": "Tipo da meditação é obrigatório"
                    },
                    "categoria": {
                        "bsonType": "string",
                        "description": "Categoria é obrigatória"
                    },
                    "imagem_capa": {
                        "bsonType": ["string", "null"],
                        "description": "URL da imagem de capa"
                    }
                }
            }
        }

        try:
            db.create_collection("meditacoes", validator=meditacoes_validator)
            print("  ✅ Coleção 'meditacoes' criada com validação de schema")
        except CollectionInvalid:
            print("  ⚠️  Coleção 'meditacoes' já existe")

        # Criar índices para meditacoes
        meditacoes_collection = db["meditacoes"]

        # Índice em categoria para filtragem
        meditacoes_collection.create_index([("categoria", ASCENDING)], name="idx_categoria")
        print("  ✅ Índice criado em 'categoria'")

        # Índice em tipo para filtragem
        meditacoes_collection.create_index([("tipo", ASCENDING)], name="idx_tipo")
        print("  ✅ Índice criado em 'tipo'")

        # Índice composto em categoria + duração
        meditacoes_collection.create_index(
            [("categoria", ASCENDING), ("duracao_minutos", ASCENDING)],
            name="idx_categoria_duracao"
        )
        print("  ✅ Índice composto criado em 'categoria + duracao_minutos'")

        # Índice de texto para busca
        meditacoes_collection.create_index(
            [("titulo", "text"), ("descricao", "text")],
            name="idx_text_search"
        )
        print("  ✅ Índice de texto criado em 'titulo + descricao'")

        # ==================== RESUMO ====================
        print("\n" + "="*60)
        print("RESUMO DA CRIAÇÃO")
        print("="*60)

        colecoes = conexao.listar_colecoes()
        print(f"\n📚 Coleções criadas: {len(colecoes)}")
        for col in colecoes:
            count = conexao.contar_documentos(col)
            print(f"  - {col}: {count} documentos")

        print("\n✅ Coleções e índices criados com sucesso!")
        print("\n💡 Próximo passo: Execute 'python scripts/migrate_postgres_to_mongo.py'")
        print("   ou insira dados manualmente através da aplicação.\n")

    except Exception as e:
        print(f"\n❌ Erro ao criar coleções: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Fecha conexão
        conexao.fechar_conexao()

if __name__ == "__main__":
    criar_colecoes()
