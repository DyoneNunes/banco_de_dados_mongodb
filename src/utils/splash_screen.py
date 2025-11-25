"""
Splash Screen - Calmou API MongoDB
Tela inicial do sistema com informações e contagem de documentos
"""

from src.conexion.mongo_conexao import MongoDBConnection
import os


class SplashScreen:
    """Classe para exibir a tela inicial do sistema"""

    def __init__(self):
        """Inicializa o splash screen"""
        self.conexao = MongoDBConnection()

    def limpar_tela(self):
        """Limpa a tela do terminal"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def exibir(self):
        """Exibe o splash screen"""
        self.limpar_tela()

        # Conta documentos
        usuarios_count = self.conexao.contar_documentos("usuarios")
        meditacoes_count = self.conexao.contar_documentos("meditacoes")

        print("\n")
        print("#" * 70)
        print("#" + " " * 68 + "#")
        print("#" + "SISTEMA CALMOU - GESTÃO DE SAÚDE MENTAL".center(68) + "#")
        print("#" + "Versão MongoDB 2.0".center(68) + "#")
        print("#" + " " * 68 + "#")
        print("#" + "-" * 68 + "#")
        print("#" + " " * 68 + "#")
        print("#" + "TOTAL DE REGISTROS EXISTENTES".center(68) + "#")
        print("#" + " " * 68 + "#")
        print("#" + f"1 - USUÁRIOS:    {usuarios_count}".center(68) + "#")
        print("#" + f"2 - MEDITAÇÕES:  {meditacoes_count}".center(68) + "#")
        print("#" + " " * 68 + "#")
        print("#" + "-" * 68 + "#")
        print("#" + " " * 68 + "#")
        print("#" + "DESENVOLVIDO POR:".center(68) + "#")
        print("#" + " " * 68 + "#")
        print("#" + "DYONE ANDRADE".center(68) + "#")
        print("#" + "[DEREK COBAIN]".center(68) + "#")
        print("#" + " " * 68 + "#")
        print("#" + "-" * 68 + "#")
        print("#" + " " * 68 + "#")
        print("#" + "DISCIPLINA: BANCO DE DADOS".center(68) + "#")
        print("#" + "PROFESSOR: HOWARD ROATTI".center(68) + "#")
        print("#" + "2025/2".center(68) + "#")
        print("#" + " " * 68 + "#")
        print("#" * 70)
        print("\n")

        input("Pressione ENTER para continuar...")


# ==================== TESTE ====================

if __name__ == "__main__":
    """Teste do splash screen"""
    splash = SplashScreen()
    splash.exibir()
