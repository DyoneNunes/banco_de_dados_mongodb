"""
Modelo de Usuário - Calmou API
Representa um usuário com dados embedded (endereço, humor, meditações, etc)
"""

from datetime import datetime
from bson import ObjectId

class Usuario:
    """Classe que representa um usuário no sistema"""

    def __init__(self, nome, email, password_hash, cpf=None, data_nascimento=None,
                 tipo_sanguineo=None, alergias=None, foto_perfil=None, config=None):
        """
        Inicializa um novo usuário

        Args:
            nome (str): Nome completo do usuário
            email (str): Email único do usuário
            password_hash (str): Hash da senha
            cpf (str, optional): CPF do usuário
            data_nascimento (datetime, optional): Data de nascimento
            tipo_sanguineo (str, optional): Tipo sanguíneo
            alergias (str, optional): Alergias do usuário
            foto_perfil (str, optional): URL da foto de perfil
            config (dict, optional): Configurações do usuário (JSON)
        """
        self._id = None
        self.nome = nome
        self.email = email
        self.password_hash = password_hash
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.tipo_sanguineo = tipo_sanguineo
        self.alergias = alergias
        self.foto_perfil = foto_perfil
        self.config = config if config else {}
        self.data_cadastro = datetime.now()

        # Subdocumentos embedded
        self.endereco = None
        self.classificacoes_humor = []
        self.historico_meditacoes = []
        self.resultados_avaliacoes = []
        self.notificacoes = []

    # ==================== GETTERS E SETTERS ====================

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = ObjectId(_id) if _id and not isinstance(_id, ObjectId) else _id

    def get_nome(self):
        return self.nome

    def set_nome(self, nome):
        self.nome = nome

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_password_hash(self):
        return self.password_hash

    def set_password_hash(self, password_hash):
        self.password_hash = password_hash

    def get_cpf(self):
        return self.cpf

    def set_cpf(self, cpf):
        self.cpf = cpf

    def get_data_nascimento(self):
        return self.data_nascimento

    def set_data_nascimento(self, data_nascimento):
        self.data_nascimento = data_nascimento

    def get_tipo_sanguineo(self):
        return self.tipo_sanguineo

    def set_tipo_sanguineo(self, tipo_sanguineo):
        self.tipo_sanguineo = tipo_sanguineo

    def get_alergias(self):
        return self.alergias

    def set_alergias(self, alergias):
        self.alergias = alergias

    def get_foto_perfil(self):
        return self.foto_perfil

    def set_foto_perfil(self, foto_perfil):
        self.foto_perfil = foto_perfil

    def get_config(self):
        return self.config

    def set_config(self, config):
        self.config = config

    def get_data_cadastro(self):
        return self.data_cadastro

    def set_data_cadastro(self, data_cadastro):
        self.data_cadastro = data_cadastro

    def get_endereco(self):
        return self.endereco

    def set_endereco(self, endereco):
        self.endereco = endereco

    def get_classificacoes_humor(self):
        return self.classificacoes_humor

    def adicionar_classificacao_humor(self, classificacao):
        """Adiciona uma classificação de humor ao array"""
        self.classificacoes_humor.append(classificacao)

    def get_historico_meditacoes(self):
        return self.historico_meditacoes

    def adicionar_historico_meditacao(self, historico):
        """Adiciona um histórico de meditação ao array"""
        self.historico_meditacoes.append(historico)

    def get_resultados_avaliacoes(self):
        return self.resultados_avaliacoes

    def adicionar_resultado_avaliacao(self, resultado):
        """Adiciona um resultado de avaliação ao array"""
        self.resultados_avaliacoes.append(resultado)

    def get_notificacoes(self):
        return self.notificacoes

    def adicionar_notificacao(self, notificacao):
        """Adiciona uma notificação ao array"""
        self.notificacoes.append(notificacao)

    # ==================== MÉTODOS DE CONVERSÃO ====================

    def to_dict(self):
        """
        Converte o objeto Usuario para um dicionário MongoDB

        Returns:
            dict: Representação do usuário para inserção no MongoDB
        """
        doc = {
            "nome": self.nome,
            "email": self.email,
            "password_hash": self.password_hash,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento,
            "tipo_sanguineo": self.tipo_sanguineo,
            "alergias": self.alergias,
            "foto_perfil": self.foto_perfil,
            "config": self.config,
            "data_cadastro": self.data_cadastro,
            "endereco": self.endereco,
            "classificacoes_humor": self.classificacoes_humor,
            "historico_meditacoes": self.historico_meditacoes,
            "resultados_avaliacoes": self.resultados_avaliacoes,
            "notificacoes": self.notificacoes
        }

        if self._id:
            doc["_id"] = self._id

        return doc

    @staticmethod
    def from_dict(doc):
        """
        Cria um objeto Usuario a partir de um documento MongoDB

        Args:
            doc (dict): Documento do MongoDB

        Returns:
            Usuario: Instância de Usuario
        """
        usuario = Usuario(
            nome=doc.get("nome"),
            email=doc.get("email"),
            password_hash=doc.get("password_hash"),
            cpf=doc.get("cpf"),
            data_nascimento=doc.get("data_nascimento"),
            tipo_sanguineo=doc.get("tipo_sanguineo"),
            alergias=doc.get("alergias"),
            foto_perfil=doc.get("foto_perfil"),
            config=doc.get("config", {})
        )

        usuario.set_id(doc.get("_id"))
        usuario.set_data_cadastro(doc.get("data_cadastro", datetime.now()))
        usuario.set_endereco(doc.get("endereco"))
        usuario.classificacoes_humor = doc.get("classificacoes_humor", [])
        usuario.historico_meditacoes = doc.get("historico_meditacoes", [])
        usuario.resultados_avaliacoes = doc.get("resultados_avaliacoes", [])
        usuario.notificacoes = doc.get("notificacoes", [])

        return usuario

    def to_string(self):
        """Representação em string do usuário"""
        return (f"Usuario(id={self._id}, nome='{self.nome}', email='{self.email}', "
                f"cpf='{self.cpf}', data_cadastro='{self.data_cadastro}')")

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


# ==================== CLASSES AUXILIARES (Subdocumentos) ====================

class Endereco:
    """Classe para representar endereço (embedded document)"""

    def __init__(self, pais, estado, cidade, rua, numero, complemento=None, cep=None):
        self.pais = pais
        self.estado = estado
        self.cidade = cidade
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.cep = cep

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "pais": self.pais,
            "estado": self.estado,
            "cidade": self.cidade,
            "rua": self.rua,
            "numero": self.numero,
            "complemento": self.complemento,
            "cep": self.cep
        }

    @staticmethod
    def from_dict(doc):
        """Cria um Endereco a partir de um dicionário"""
        if not doc:
            return None
        return Endereco(
            pais=doc.get("pais"),
            estado=doc.get("estado"),
            cidade=doc.get("cidade"),
            rua=doc.get("rua"),
            numero=doc.get("numero"),
            complemento=doc.get("complemento"),
            cep=doc.get("cep")
        )

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade}/{self.estado}"


class ClassificacaoHumor:
    """Classe para representar classificação de humor (embedded document)"""

    def __init__(self, nivel_humor, sentimento_principal, notas=None, data_classificacao=None):
        self.nivel_humor = nivel_humor
        self.sentimento_principal = sentimento_principal
        self.notas = notas
        self.data_classificacao = data_classificacao if data_classificacao else datetime.now()

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "nivel_humor": self.nivel_humor,
            "sentimento_principal": self.sentimento_principal,
            "notas": self.notas,
            "data_classificacao": self.data_classificacao
        }

    def __str__(self):
        return f"Humor: {self.nivel_humor}/5 - {self.sentimento_principal}"


class HistoricoMeditacao:
    """Classe para representar histórico de meditação (embedded document)"""

    def __init__(self, meditacao_id, data_conclusao=None, duracao_real_minutos=None):
        self.meditacao_id = ObjectId(meditacao_id) if not isinstance(meditacao_id, ObjectId) else meditacao_id
        self.data_conclusao = data_conclusao if data_conclusao else datetime.now()
        self.duracao_real_minutos = duracao_real_minutos

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "meditacao_id": self.meditacao_id,
            "data_conclusao": self.data_conclusao,
            "duracao_real_minutos": self.duracao_real_minutos
        }

    def __str__(self):
        return f"Meditação concluída em {self.data_conclusao}"


class ResultadoAvaliacao:
    """Classe para representar resultado de avaliação (embedded document)"""

    def __init__(self, tipo, respostas, resultado_score, resultado_texto, data_avaliacao=None):
        self.tipo = tipo  # ansiedade, depressão, estresse, burnout
        self.respostas = respostas  # Dicionário com as respostas
        self.resultado_score = resultado_score
        self.resultado_texto = resultado_texto
        self.data_avaliacao = data_avaliacao if data_avaliacao else datetime.now()

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "tipo": self.tipo,
            "respostas": self.respostas,
            "resultado_score": self.resultado_score,
            "resultado_texto": self.resultado_texto,
            "data_avaliacao": self.data_avaliacao
        }

    def __str__(self):
        return f"Avaliação de {self.tipo}: {self.resultado_score} - {self.resultado_texto}"


class Notificacao:
    """Classe para representar notificação (embedded document)"""

    def __init__(self, titulo, mensagem, data_envio=None, lida=False):
        self.titulo = titulo
        self.mensagem = mensagem
        self.data_envio = data_envio if data_envio else datetime.now()
        self.lida = lida

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "titulo": self.titulo,
            "mensagem": self.mensagem,
            "data_envio": self.data_envio,
            "lida": self.lida
        }

    def __str__(self):
        status = "✓ Lida" if self.lida else "✗ Não lida"
        return f"{self.titulo} ({status})"
