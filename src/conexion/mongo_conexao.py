"""
Módulo de Conexão com MongoDB
Gerencia a conexão singleton com o banco de dados MongoDB
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class MongoDBConnection:
    """
    Classe singleton para gerenciar conexão com MongoDB
    """
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        """Implementa o padrão Singleton"""
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa a conexão apenas uma vez"""
        if self._client is None:
            self._conectar()

    def _conectar(self):
        """Estabelece conexão com o MongoDB"""
        try:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            db_name = os.getenv("MONGO_DB_NAME", "calmou_db")

            # Configurações de timeout
            self._client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 segundos
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )

            # Testa a conexão
            self._client.admin.command('ping')

            # Seleciona o banco de dados
            self._db = self._client[db_name]

            print(f"✅ Conectado ao MongoDB: {db_name}")

        except ConnectionFailure as e:
            print(f"❌ Erro ao conectar ao MongoDB: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            print(f"❌ Timeout ao conectar ao MongoDB. Verifique se o MongoDB está rodando.")
            raise
        except Exception as e:
            print(f"❌ Erro inesperado ao conectar: {e}")
            raise

    def get_database(self):
        """
        Retorna a instância do banco de dados

        Returns:
            Database: Objeto de banco de dados do MongoDB
        """
        if self._db is None:
            self._conectar()
        return self._db

    def get_collection(self, collection_name):
        """
        Retorna uma coleção específica

        Args:
            collection_name (str): Nome da coleção

        Returns:
            Collection: Objeto de coleção do MongoDB
        """
        return self._db[collection_name]

    def fechar_conexao(self):
        """Fecha a conexão com o MongoDB"""
        if self._client:
            self._client.close()
            print("🔌 Conexão com MongoDB fechada")

    def contar_documentos(self, collection_name):
        """
        Conta o número de documentos em uma coleção

        Args:
            collection_name (str): Nome da coleção

        Returns:
            int: Número de documentos
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.count_documents({})
        except Exception as e:
            print(f"❌ Erro ao contar documentos na coleção {collection_name}: {e}")
            return 0

    def listar_colecoes(self):
        """
        Lista todas as coleções do banco de dados

        Returns:
            list: Lista com nomes das coleções
        """
        try:
            return self._db.list_collection_names()
        except Exception as e:
            print(f"❌ Erro ao listar coleções: {e}")
            return []

    def resetar_colecao(self, collection_name):
        """
        Remove todos os documentos de uma coleção (use com cuidado!)

        Args:
            collection_name (str): Nome da coleção
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many({})
            print(f"🗑️  {result.deleted_count} documentos removidos de {collection_name}")
        except Exception as e:
            print(f"❌ Erro ao resetar coleção {collection_name}: {e}")

# ==================== FUNÇÕES DE CONVENIÊNCIA ====================

def conectar_mongo():
    """
    Função de conveniência para obter o banco de dados

    Returns:
        Database: Instância do banco de dados MongoDB
    """
    conexao = MongoDBConnection()
    return conexao.get_database()

def fechar_mongo():
    """Função de conveniência para fechar a conexão"""
    conexao = MongoDBConnection()
    conexao.fechar_conexao()

def obter_colecao(collection_name):
    """
    Função de conveniência para obter uma coleção

    Args:
        collection_name (str): Nome da coleção

    Returns:
        Collection: Objeto de coleção do MongoDB
    """
    conexao = MongoDBConnection()
    return conexao.get_collection(collection_name)

# ==================== TESTE DE CONEXÃO ====================

if __name__ == "__main__":
    """Teste de conexão ao MongoDB"""
    print("\n" + "="*50)
    print("TESTE DE CONEXÃO MongoDB")
    print("="*50 + "\n")

    try:
        # Testa conexão
        db = conectar_mongo()

        # Lista coleções
        conexao = MongoDBConnection()
        colecoes = conexao.listar_colecoes()

        print(f"\n📚 Coleções existentes: {colecoes if colecoes else 'Nenhuma'}")

        # Conta documentos
        if colecoes:
            print("\n📊 Contagem de documentos:")
            for col in colecoes:
                count = conexao.contar_documentos(col)
                print(f"  - {col}: {count} documentos")

        print("\n✅ Teste concluído com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
    finally:
        fechar_mongo()
