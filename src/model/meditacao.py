"""
Modelo de Meditação - Calmou API
Representa uma meditação disponível no catálogo
"""

from bson import ObjectId

class Meditacao:
    """Classe que representa uma meditação no sistema"""

    def __init__(self, titulo, descricao, duracao_minutos, url_audio,
                 tipo, categoria, imagem_capa=None):
        """
        Inicializa uma nova meditação

        Args:
            titulo (str): Título da meditação
            descricao (str): Descrição detalhada
            duracao_minutos (int): Duração em minutos
            url_audio (str): URL do arquivo de áudio
            tipo (str): Tipo da meditação (respiração, mindfulness, etc)
            categoria (str): Categoria (iniciante, intermediário, avançado)
            imagem_capa (str, optional): URL da imagem de capa
        """
        self._id = None
        self.titulo = titulo
        self.descricao = descricao
        self.duracao_minutos = duracao_minutos
        self.url_audio = url_audio
        self.tipo = tipo
        self.categoria = categoria
        self.imagem_capa = imagem_capa

    # ==================== GETTERS E SETTERS ====================

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = ObjectId(_id) if _id and not isinstance(_id, ObjectId) else _id

    def get_titulo(self):
        return self.titulo

    def set_titulo(self, titulo):
        self.titulo = titulo

    def get_descricao(self):
        return self.descricao

    def set_descricao(self, descricao):
        self.descricao = descricao

    def get_duracao_minutos(self):
        return self.duracao_minutos

    def set_duracao_minutos(self, duracao_minutos):
        self.duracao_minutos = duracao_minutos

    def get_url_audio(self):
        return self.url_audio

    def set_url_audio(self, url_audio):
        self.url_audio = url_audio

    def get_tipo(self):
        return self.tipo

    def set_tipo(self, tipo):
        self.tipo = tipo

    def get_categoria(self):
        return self.categoria

    def set_categoria(self, categoria):
        self.categoria = categoria

    def get_imagem_capa(self):
        return self.imagem_capa

    def set_imagem_capa(self, imagem_capa):
        self.imagem_capa = imagem_capa

    # ==================== MÉTODOS DE CONVERSÃO ====================

    def to_dict(self):
        """
        Converte o objeto Meditacao para um dicionário MongoDB

        Returns:
            dict: Representação da meditação para inserção no MongoDB
        """
        doc = {
            "titulo": self.titulo,
            "descricao": self.descricao,
            "duracao_minutos": self.duracao_minutos,
            "url_audio": self.url_audio,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "imagem_capa": self.imagem_capa
        }

        if self._id:
            doc["_id"] = self._id

        return doc

    @staticmethod
    def from_dict(doc):
        """
        Cria um objeto Meditacao a partir de um documento MongoDB

        Args:
            doc (dict): Documento do MongoDB

        Returns:
            Meditacao: Instância de Meditacao
        """
        if not doc:
            return None

        meditacao = Meditacao(
            titulo=doc.get("titulo"),
            descricao=doc.get("descricao"),
            duracao_minutos=doc.get("duracao_minutos"),
            url_audio=doc.get("url_audio"),
            tipo=doc.get("tipo"),
            categoria=doc.get("categoria"),
            imagem_capa=doc.get("imagem_capa")
        )

        meditacao.set_id(doc.get("_id"))

        return meditacao

    def to_string(self):
        """Representação em string da meditação"""
        return (f"Meditacao(id={self._id}, titulo='{self.titulo}', "
                f"tipo='{self.tipo}', duracao={self.duracao_minutos}min, "
                f"categoria='{self.categoria}')")

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
