"""
Controller de Usuários - Calmou API
Gerencia operações CRUD para usuários no MongoDB
"""

from bson import ObjectId
from bson.errors import InvalidId
from src.conexion.mongo_conexao import obter_colecao
from src.model.usuario import Usuario, ClassificacaoHumor, HistoricoMeditacao, ResultadoAvaliacao, Notificacao
from datetime import datetime


class ControllerUsuario:
    """Controlador para operações CRUD de usuários"""

    def __init__(self):
        """Inicializa o controller"""
        self.collection = obter_colecao("usuarios")

    # ==================== CREATE ====================

    def inserir_usuario(self, usuario):
        """
        Insere um novo usuário no MongoDB

        Args:
            usuario (Usuario): Objeto Usuario

        Returns:
            ObjectId: ID do usuário inserido, ou None se falhar
        """
        try:
            # Verifica se email já existe
            if self.buscar_por_email(usuario.get_email()):
                print(f"❌ Erro: Email '{usuario.get_email()}' já cadastrado")
                return None

            # Verifica se CPF já existe (se fornecido)
            if usuario.get_cpf() and self.buscar_por_cpf(usuario.get_cpf()):
                print(f"❌ Erro: CPF '{usuario.get_cpf()}' já cadastrado")
                return None

            # Insere o usuário
            resultado = self.collection.insert_one(usuario.to_dict())
            print(f"✅ Usuário '{usuario.get_nome()}' inserido com sucesso")
            return resultado.inserted_id

        except Exception as e:
            print(f"❌ Erro ao inserir usuário: {e}")
            return None

    # ==================== READ ====================

    def buscar_por_id(self, usuario_id):
        """
        Busca um usuário por ID

        Args:
            usuario_id (str ou ObjectId): ID do usuário

        Returns:
            Usuario ou None: Objeto Usuario ou None se não encontrado
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)

            doc = self.collection.find_one({"_id": usuario_id})

            if doc:
                return Usuario.from_dict(doc)
            return None

        except InvalidId:
            print(f"❌ ID inválido: {usuario_id}")
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar usuário por ID: {e}")
            return None

    def buscar_por_email(self, email):
        """
        Busca um usuário por email

        Args:
            email (str): Email do usuário

        Returns:
            Usuario ou None: Objeto Usuario ou None se não encontrado
        """
        try:
            doc = self.collection.find_one({"email": email})

            if doc:
                return Usuario.from_dict(doc)
            return None

        except Exception as e:
            print(f"❌ Erro ao buscar usuário por email: {e}")
            return None

    def buscar_por_cpf(self, cpf):
        """
        Busca um usuário por CPF

        Args:
            cpf (str): CPF do usuário

        Returns:
            Usuario ou None: Objeto Usuario ou None se não encontrado
        """
        try:
            doc = self.collection.find_one({"cpf": cpf})

            if doc:
                return Usuario.from_dict(doc)
            return None

        except Exception as e:
            print(f"❌ Erro ao buscar usuário por CPF: {e}")
            return None

    def listar_todos(self, limite=100):
        """
        Lista todos os usuários

        Args:
            limite (int): Limite de resultados

        Returns:
            list: Lista de objetos Usuario
        """
        try:
            docs = self.collection.find().sort("data_cadastro", -1).limit(limite)
            return [Usuario.from_dict(doc) for doc in docs]

        except Exception as e:
            print(f"❌ Erro ao listar usuários: {e}")
            return []

    def listar_resumo(self, limite=100):
        """
        Lista resumo dos usuários (apenas campos principais)

        Args:
            limite (int): Limite de resultados

        Returns:
            list: Lista de dicionários com dados resumidos
        """
        try:
            docs = self.collection.find(
                {},
                {"_id": 1, "nome": 1, "email": 1, "cpf": 1, "data_cadastro": 1}
            ).sort("data_cadastro", -1).limit(limite)

            return list(docs)

        except Exception as e:
            print(f"❌ Erro ao listar resumo de usuários: {e}")
            return []

    # ==================== UPDATE ====================

    def atualizar_usuario(self, usuario_id, campos_atualizados):
        """
        Atualiza campos de um usuário

        Args:
            usuario_id (str ou ObjectId): ID do usuário
            campos_atualizados (dict): Dicionário com campos a atualizar

        Returns:
            bool: True se atualizado, False caso contrário
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)

            # Verifica se usuário existe
            if not self.buscar_por_id(usuario_id):
                print(f"❌ Usuário com ID {usuario_id} não encontrado")
                return False

            # Remove _id dos campos (não pode ser atualizado)
            campos_atualizados.pop("_id", None)

            # Atualiza
            resultado = self.collection.update_one(
                {"_id": usuario_id},
                {"$set": campos_atualizados}
            )

            if resultado.modified_count > 0:
                print(f"✅ Usuário {usuario_id} atualizado com sucesso")
                return True
            else:
                print(f"⚠️  Nenhuma modificação realizada (valores podem ser iguais)")
                return True

        except Exception as e:
            print(f"❌ Erro ao atualizar usuário: {e}")
            return False

    # ==================== DELETE ====================

    def remover_usuario(self, usuario_id):
        """
        Remove um usuário

        Args:
            usuario_id (str ou ObjectId): ID do usuário

        Returns:
            bool: True se removido, False caso contrário
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)

            # Verifica se usuário existe
            usuario = self.buscar_por_id(usuario_id)
            if not usuario:
                print(f"❌ Usuário com ID {usuario_id} não encontrado")
                return False

            # Remove
            resultado = self.collection.delete_one({"_id": usuario_id})

            if resultado.deleted_count > 0:
                print(f"✅ Usuário '{usuario.get_nome()}' removido com sucesso")
                return True
            else:
                print(f"❌ Falha ao remover usuário")
                return False

        except Exception as e:
            print(f"❌ Erro ao remover usuário: {e}")
            return False

    # ==================== OPERAÇÕES COM SUBDOCUMENTOS ====================

    def adicionar_classificacao_humor(self, usuario_id, classificacao):
        """
        Adiciona uma classificação de humor ao usuário

        Args:
            usuario_id (str ou ObjectId): ID do usuário
            classificacao (ClassificacaoHumor): Objeto de classificação

        Returns:
            bool: True se adicionado, False caso contrário
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)

            resultado = self.collection.update_one(
                {"_id": usuario_id},
                {"$push": {"classificacoes_humor": classificacao.to_dict()}}
            )

            if resultado.modified_count > 0:
                print(f"✅ Classificação de humor adicionada")
                return True
            return False

        except Exception as e:
            print(f"❌ Erro ao adicionar classificação: {e}")
            return False

    def adicionar_historico_meditacao(self, usuario_id, historico):
        """
        Adiciona um histórico de meditação ao usuário

        Args:
            usuario_id (str ou ObjectId): ID do usuário
            historico (HistoricoMeditacao): Objeto de histórico

        Returns:
            bool: True se adicionado, False caso contrário
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)

            resultado = self.collection.update_one(
                {"_id": usuario_id},
                {"$push": {"historico_meditacoes": historico.to_dict()}}
            )

            if resultado.modified_count > 0:
                print(f"✅ Histórico de meditação adicionado")
                return True
            return False

        except Exception as e:
            print(f"❌ Erro ao adicionar histórico: {e}")
            return False

    def adicionar_resultado_avaliacao(self, usuario_id, resultado_aval):
        """
        Adiciona um resultado de avaliação ao usuário

        Args:
            usuario_id (str ou ObjectId): ID do usuário
            resultado_aval (ResultadoAvaliacao): Objeto de resultado

        Returns:
            bool: True se adicionado, False caso contrário
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)

            resultado = self.collection.update_one(
                {"_id": usuario_id},
                {"$push": {"resultados_avaliacoes": resultado_aval.to_dict()}}
            )

            if resultado.modified_count > 0:
                print(f"✅ Resultado de avaliação adicionado")
                return True
            return False

        except Exception as e:
            print(f"❌ Erro ao adicionar resultado: {e}")
            return False

    def adicionar_notificacao(self, usuario_id, notificacao):
        """
        Adiciona uma notificação ao usuário

        Args:
            usuario_id (str ou ObjectId): ID do usuário
            notificacao (Notificacao): Objeto de notificação

        Returns:
            bool: True se adicionado, False caso contrário
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)

            resultado = self.collection.update_one(
                {"_id": usuario_id},
                {"$push": {"notificacoes": notificacao.to_dict()}}
            )

            if resultado.modified_count > 0:
                print(f"✅ Notificação adicionada")
                return True
            return False

        except Exception as e:
            print(f"❌ Erro ao adicionar notificação: {e}")
            return False

    # ==================== CONTADORES ====================

    def contar_todos(self):
        """
        Conta o total de usuários

        Returns:
            int: Número total de usuários
        """
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"❌ Erro ao contar usuários: {e}")
            return 0
