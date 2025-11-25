"""
Script de Migração PostgreSQL → MongoDB - Calmou API
Migra dados do PostgreSQL (meu_banco) para MongoDB (calmou_db)
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psycopg2
    from psycopg2 import sql
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  psycopg2 não está instalado. Instale com: pip install psycopg2-binary")

from src.conexion.mongo_conexao import MongoDBConnection
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def conectar_postgresql():
    """Conecta ao PostgreSQL"""
    try:
        conn = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB")
        )
        print("✅ Conectado ao PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return None

def migrar_meditacoes(pg_conn, mongo_conn):
    """
    Migra meditações do PostgreSQL para MongoDB

    Returns:
        dict: Mapeamento de ID PostgreSQL → ObjectId MongoDB
    """
    print("\n1️⃣ Migrando meditações...")

    try:
        cursor = pg_conn.cursor()
        cursor.execute("SELECT * FROM meditacoes ORDER BY id")
        meditacoes_pg = cursor.fetchall()

        meditacoes_collection = mongo_conn.get_collection("meditacoes")
        meditacoes_map = {}

        for med in meditacoes_pg:
            med_doc = {
                "titulo": med[1],
                "descricao": med[2],
                "duracao_minutos": med[3],
                "url_audio": med[4],
                "tipo": med[5],
                "categoria": med[6],
                "imagem_capa": med[7] if len(med) > 7 else None
            }

            result = meditacoes_collection.insert_one(med_doc)
            meditacoes_map[med[0]] = result.inserted_id

        print(f"  ✅ {len(meditacoes_pg)} meditações migradas")
        cursor.close()
        return meditacoes_map

    except Exception as e:
        print(f"  ❌ Erro ao migrar meditações: {e}")
        return {}

def migrar_usuarios(pg_conn, mongo_conn, meditacoes_map):
    """
    Migra usuários e todos os dados relacionados (embedded)

    Args:
        pg_conn: Conexão PostgreSQL
        mongo_conn: Conexão MongoDB
        meditacoes_map: Mapeamento de IDs de meditações
    """
    print("\n2️⃣ Migrando usuários e dados relacionados...")

    try:
        cursor = pg_conn.cursor()
        cursor.execute("SELECT * FROM usuarios ORDER BY id")
        usuarios_pg = cursor.fetchall()

        usuarios_collection = mongo_conn.get_collection("usuarios")
        usuarios_migrados = 0

        for user in usuarios_pg:
            user_id = user[0]

            # Dados básicos do usuário
            user_doc = {
                "nome": user[1],
                "email": user[2],
                "password_hash": user[3],
                "config": user[4] if user[4] else {},
                "data_cadastro": user[5] if user[5] else datetime.now(),
                "cpf": user[6] if len(user) > 6 else None,
                "data_nascimento": user[7] if len(user) > 7 else None,
                "tipo_sanguineo": user[8] if len(user) > 8 else None,
                "alergias": user[9] if len(user) > 9 else None,
                "foto_perfil": user[10] if len(user) > 10 else None
            }

            # ==================== BUSCAR ENDEREÇO ====================
            cursor_end = pg_conn.cursor()
            cursor_end.execute("SELECT * FROM enderecos WHERE usuario_id = %s", (user_id,))
            endereco = cursor_end.fetchone()

            if endereco:
                user_doc["endereco"] = {
                    "pais": endereco[2],
                    "estado": endereco[3],
                    "cidade": endereco[4],
                    "rua": endereco[5],
                    "numero": endereco[6],
                    "complemento": endereco[7],
                    "cep": endereco[8]
                }
            else:
                user_doc["endereco"] = None

            cursor_end.close()

            # ==================== BUSCAR CLASSIFICAÇÕES DE HUMOR ====================
            cursor_humor = pg_conn.cursor()
            cursor_humor.execute(
                "SELECT * FROM classificacoes_humor WHERE usuario_id = %s ORDER BY data_classificacao DESC",
                (user_id,)
            )
            humores = cursor_humor.fetchall()
            user_doc["classificacoes_humor"] = [
                {
                    "nivel_humor": h[2],
                    "sentimento_principal": h[3],
                    "notas": h[4],
                    "data_classificacao": h[5] if h[5] else datetime.now()
                } for h in humores
            ]
            cursor_humor.close()

            # ==================== BUSCAR HISTÓRICO DE MEDITAÇÕES ====================
            cursor_hist = pg_conn.cursor()
            cursor_hist.execute(
                "SELECT * FROM historico_meditacoes WHERE usuario_id = %s ORDER BY data_conclusao DESC",
                (user_id,)
            )
            historicos = cursor_hist.fetchall()
            user_doc["historico_meditacoes"] = []

            for h in historicos:
                meditacao_id_pg = h[2]
                meditacao_id_mongo = meditacoes_map.get(meditacao_id_pg)

                if meditacao_id_mongo:
                    user_doc["historico_meditacoes"].append({
                        "meditacao_id": meditacao_id_mongo,
                        "data_conclusao": h[3] if h[3] else datetime.now(),
                        "duracao_real_minutos": h[4]
                    })

            cursor_hist.close()

            # ==================== BUSCAR RESULTADOS DE AVALIAÇÕES ====================
            cursor_aval = pg_conn.cursor()
            cursor_aval.execute(
                "SELECT * FROM resultados_avaliacoes WHERE usuario_id = %s ORDER BY data_avaliacao DESC",
                (user_id,)
            )
            avaliacoes = cursor_aval.fetchall()
            user_doc["resultados_avaliacoes"] = [
                {
                    "tipo": a[2],
                    "respostas": a[3] if a[3] else {},
                    "resultado_score": a[4],
                    "resultado_texto": a[5],
                    "data_avaliacao": a[6] if a[6] else datetime.now()
                } for a in avaliacoes
            ]
            cursor_aval.close()

            # ==================== BUSCAR NOTIFICAÇÕES ====================
            cursor_notif = pg_conn.cursor()
            cursor_notif.execute(
                "SELECT * FROM notificacoes WHERE usuario_id = %s ORDER BY data_envio DESC",
                (user_id,)
            )
            notificacoes = cursor_notif.fetchall()
            user_doc["notificacoes"] = [
                {
                    "titulo": n[2],
                    "mensagem": n[3],
                    "data_envio": n[4] if n[4] else datetime.now(),
                    "lida": n[5] if len(n) > 5 else False
                } for n in notificacoes
            ]
            cursor_notif.close()

            # ==================== INSERIR USUÁRIO NO MONGODB ====================
            usuarios_collection.insert_one(user_doc)
            usuarios_migrados += 1

        print(f"  ✅ {usuarios_migrados} usuários migrados com dados relacionados")
        cursor.close()

    except Exception as e:
        print(f"  ❌ Erro ao migrar usuários: {e}")
        import traceback
        traceback.print_exc()

def migrar_dados():
    """Função principal de migração"""

    print("\n" + "="*60)
    print("MIGRAÇÃO POSTGRESQL → MONGODB - CALMOU API")
    print("="*60 + "\n")

    if not POSTGRES_AVAILABLE:
        print("❌ Migração cancelada: psycopg2 não disponível")
        return

    # Conectar ao PostgreSQL
    pg_conn = conectar_postgresql()
    if not pg_conn:
        print("❌ Migração cancelada: Falha ao conectar ao PostgreSQL")
        return

    # Conectar ao MongoDB
    mongo_conn = MongoDBConnection()
    print("✅ Conectado ao MongoDB")

    try:
        # Migrar meditações primeiro (para obter mapeamento de IDs)
        meditacoes_map = migrar_meditacoes(pg_conn, mongo_conn)

        # Migrar usuários com todos os dados relacionados
        migrar_usuarios(pg_conn, mongo_conn, meditacoes_map)

        # ==================== RESUMO ====================
        print("\n" + "="*60)
        print("RESUMO DA MIGRAÇÃO")
        print("="*60)

        meditacoes_count = mongo_conn.contar_documentos("meditacoes")
        usuarios_count = mongo_conn.contar_documentos("usuarios")

        print(f"\n📊 Dados migrados:")
        print(f"  - Meditações: {meditacoes_count}")
        print(f"  - Usuários: {usuarios_count}")

        print("\n✅ Migração concluída com sucesso!")
        print("\n💡 Próximo passo: Execute 'python principal.py' para usar o sistema.\n")

    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Fechar conexões
        if pg_conn:
            pg_conn.close()
            print("\n🔌 Conexão PostgreSQL fechada")
        mongo_conn.fechar_conexao()

if __name__ == "__main__":
    # Confirmar migração
    print("\n⚠️  ATENÇÃO: Este script irá migrar dados do PostgreSQL para MongoDB")
    print("Certifique-se de que:")
    print("  1. O MongoDB está rodando")
    print("  2. O PostgreSQL está acessível")
    print("  3. As variáveis de ambiente estão configuradas no .env")
    print("  4. Você executou 'python scripts/create_collections.py' antes\n")

    resposta = input("Deseja continuar? (s/N): ").strip().lower()

    if resposta == 's' or resposta == 'sim':
        migrar_dados()
    else:
        print("\n❌ Migração cancelada pelo usuário")
