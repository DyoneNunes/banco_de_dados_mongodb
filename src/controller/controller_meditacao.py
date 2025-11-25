"""
Controller de Meditações - Calmou API
Gerencia operações CRUD para meditações no MongoDB
"""

from bson import ObjectId
from bson.errors import InvalidId
from src.conexion.mongo_conexao import obter_colecao
from src.model.meditacao import Meditacao


class ControllerMeditacao:
    """Controlador para operações CRUD de meditações"""

    def __init__(self):
        """Inicializa o controller"""
        self.collection = obter_colecao("meditacoes")

    # ==================== CREATE ====================

    def inserir_meditacao(self, meditacao):
        """
        Insere uma nova meditação no MongoDB

        Args:
            meditacao (Meditacao): Objeto Meditacao

        Returns:
            ObjectId: ID da meditação inserida, ou None se falhar
        """
        try:
            # Verifica se já existe meditação com mesmo título
            if self.buscar_por_titulo(meditacao.get_titulo()):
                print(f"⚠️  Atenção: Já existe uma meditação com o título '{meditacao.get_titulo()}'")
                resposta = input("Deseja inserir mesmo assim? (s/N): ").strip().lower()
                if resposta != 's' and resposta != 'sim':
                    print("❌ Inserção cancelada")
                    return None

            # Insere a meditação
            resultado = self.collection.insert_one(meditacao.to_dict())
            print(f"✅ Meditação '{meditacao.get_titulo()}' inserida com sucesso")
            return resultado.inserted_id

        except Exception as e:
            print(f"❌ Erro ao inserir meditação: {e}")
            return None

    # ==================== READ ====================

    def buscar_por_id(self, meditacao_id):
        """
        Busca uma meditação por ID

        Args:
            meditacao_id (str ou ObjectId): ID da meditação

        Returns:
            Meditacao ou None: Objeto Meditacao ou None se não encontrado
        """
        try:
            if isinstance(meditacao_id, str):
                meditacao_id = ObjectId(meditacao_id)

            doc = self.collection.find_one({"_id": meditacao_id})

            if doc:
                return Meditacao.from_dict(doc)
            return None

        except InvalidId:
            print(f"❌ ID inválido: {meditacao_id}")
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar meditação por ID: {e}")
            return None

    def buscar_por_titulo(self, titulo):
        """
        Busca uma meditação por título (primeira ocorrência)

        Args:
            titulo (str): Título da meditação

        Returns:
            Meditacao ou None: Objeto Meditacao ou None se não encontrado
        """
        try:
            doc = self.collection.find_one({"titulo": titulo})

            if doc:
                return Meditacao.from_dict(doc)
            return None

        except Exception as e:
            print(f"❌ Erro ao buscar meditação por título: {e}")
            return None

    def listar_todas(self, limite=100):
        """
        Lista todas as meditações

        Args:
            limite (int): Limite de resultados

        Returns:
            list: Lista de objetos Meditacao
        """
        try:
            docs = self.collection.find().sort("titulo", 1).limit(limite)
            return [Meditacao.from_dict(doc) for doc in docs]

        except Exception as e:
            print(f"❌ Erro ao listar meditações: {e}")
            return []

    def listar_resumo(self, limite=100):
        """
        Lista resumo das meditações (apenas campos principais)

        Args:
            limite (int): Limite de resultados

        Returns:
            list: Lista de dicionários com dados resumidos
        """
        try:
            docs = self.collection.find(
                {},
                {"_id": 1, "titulo": 1, "tipo": 1, "categoria": 1, "duracao_minutos": 1}
            ).sort("titulo", 1).limit(limite)

            return list(docs)

        except Exception as e:
            print(f"❌ Erro ao listar resumo de meditações: {e}")
            return []

    def buscar_por_categoria(self, categoria, limite=100):
        """
        Busca meditações por categoria

        Args:
            categoria (str): Categoria (iniciante, intermediário, avançado)
            limite (int): Limite de resultados

        Returns:
            list: Lista de objetos Meditacao
        """
        try:
            docs = self.collection.find({"categoria": categoria}).sort("titulo", 1).limit(limite)
            return [Meditacao.from_dict(doc) for doc in docs]

        except Exception as e:
            print(f"❌ Erro ao buscar por categoria: {e}")
            return []

    def buscar_por_tipo(self, tipo, limite=100):
        """
        Busca meditações por tipo

        Args:
            tipo (str): Tipo da meditação
            limite (int): Limite de resultados

        Returns:
            list: Lista de objetos Meditacao
        """
        try:
            docs = self.collection.find({"tipo": tipo}).sort("titulo", 1).limit(limite)
            return [Meditacao.from_dict(doc) for doc in docs]

        except Exception as e:
            print(f"❌ Erro ao buscar por tipo: {e}")
            return []

    def buscar_por_duracao(self, duracao_min, duracao_max, limite=100):
        """
        Busca meditações por faixa de duração

        Args:
            duracao_min (int): Duração mínima em minutos
            duracao_max (int): Duração máxima em minutos
            limite (int): Limite de resultados

        Returns:
            list: Lista de objetos Meditacao
        """
        try:
            docs = self.collection.find({
                "duracao_minutos": {"$gte": duracao_min, "$lte": duracao_max}
            }).sort("duracao_minutos", 1).limit(limite)

            return [Meditacao.from_dict(doc) for doc in docs]

        except Exception as e:
            print(f"❌ Erro ao buscar por duração: {e}")
            return []

    # ==================== UPDATE ====================

    def atualizar_meditacao(self, meditacao_id, campos_atualizados):
        """
        Atualiza campos de uma meditação

        Args:
            meditacao_id (str ou ObjectId): ID da meditação
            campos_atualizados (dict): Dicionário com campos a atualizar

        Returns:
            bool: True se atualizado, False caso contrário
        """
        try:
            if isinstance(meditacao_id, str):
                meditacao_id = ObjectId(meditacao_id)

            # Verifica se meditação existe
            if not self.buscar_por_id(meditacao_id):
                print(f"❌ Meditação com ID {meditacao_id} não encontrada")
                return False

            # Remove _id dos campos (não pode ser atualizado)
            campos_atualizados.pop("_id", None)

            # Atualiza
            resultado = self.collection.update_one(
                {"_id": meditacao_id},
                {"$set": campos_atualizados}
            )

            if resultado.modified_count > 0:
                print(f"✅ Meditação {meditacao_id} atualizada com sucesso")
                return True
            else:
                print(f"⚠️  Nenhuma modificação realizada (valores podem ser iguais)")
                return True

        except Exception as e:
            print(f"❌ Erro ao atualizar meditação: {e}")
            return False

    # ==================== DELETE ====================

    def remover_meditacao(self, meditacao_id):
        """
        Remove uma meditação

        ATENÇÃO: Verifica se há usuários com histórico desta meditação

        Args:
            meditacao_id (str ou ObjectId): ID da meditação

        Returns:
            bool: True se removido, False caso contrário
        """
        try:
            if isinstance(meditacao_id, str):
                meditacao_id = ObjectId(meditacao_id)

            # Verifica se meditação existe
            meditacao = self.buscar_por_id(meditacao_id)
            if not meditacao:
                print(f"❌ Meditação com ID {meditacao_id} não encontrada")
                return False

            # Verifica se há usuários com histórico desta meditação
            usuarios_collection = obter_colecao("usuarios")
            usuarios_com_historico = usuarios_collection.count_documents({
                "historico_meditacoes.meditacao_id": meditacao_id
            })

            if usuarios_com_historico > 0:
                print(f"\n⚠️  ATENÇÃO: {usuarios_com_historico} usuário(s) têm histórico desta meditação")
                print("Opções:")
                print("  1 - Remover meditação e manter referências no histórico (pode causar inconsistências)")
                print("  2 - Remover meditação e APAGAR históricos de todos os usuários")
                print("  3 - Cancelar remoção")

                escolha = input("\nEscolha uma opção (1/2/3): ").strip()

                if escolha == '1':
                    # Remove apenas a meditação
                    pass
                elif escolha == '2':
                    # Remove meditação e históricos
                    usuarios_collection.update_many(
                        {},
                        {"$pull": {"historico_meditacoes": {"meditacao_id": meditacao_id}}}
                    )
                    print(f"✅ Históricos removidos de {usuarios_com_historico} usuário(s)")
                else:
                    print("❌ Remoção cancelada")
                    return False

            # Remove a meditação
            resultado = self.collection.delete_one({"_id": meditacao_id})

            if resultado.deleted_count > 0:
                print(f"✅ Meditação '{meditacao.get_titulo()}' removida com sucesso")
                return True
            else:
                print(f"❌ Falha ao remover meditação")
                return False

        except Exception as e:
            print(f"❌ Erro ao remover meditação: {e}")
            return False

    # ==================== CONTADORES ====================

    def contar_todas(self):
        """
        Conta o total de meditações

        Returns:
            int: Número total de meditações
        """
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"❌ Erro ao contar meditações: {e}")
            return 0

    def contar_por_categoria(self):
        """
        Conta meditações por categoria

        Returns:
            dict: Dicionário com contagem por categoria
        """
        try:
            pipeline = [
                {"$group": {"_id": "$categoria", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]

            resultado = list(self.collection.aggregate(pipeline))
            return {item["_id"]: item["count"] for item in resultado}

        except Exception as e:
            print(f"❌ Erro ao contar por categoria: {e}")
            return {}

    def contar_por_tipo(self):
        """
        Conta meditações por tipo

        Returns:
            dict: Dicionário com contagem por tipo
        """
        try:
            pipeline = [
                {"$group": {"_id": "$tipo", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]

            resultado = list(self.collection.aggregate(pipeline))
            return {item["_id"]: item["count"] for item in resultado}

        except Exception as e:
            print(f"❌ Erro ao contar por tipo: {e}")
            return {}
