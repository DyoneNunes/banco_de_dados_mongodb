"""
Configurações e Menus - Calmou API MongoDB
Define os menus e configurações do sistema
"""

# ==================== MENUS ====================

MENU_PRINCIPAL = """
╔═══════════════════════════════════════════════════════════╗
║              MENU PRINCIPAL - SISTEMA CALMOU              ║
╚═══════════════════════════════════════════════════════════╝

  1 - Relatórios
  2 - Gerenciar Usuários
  3 - Gerenciar Meditações
  0 - Sair

"""

MENU_USUARIOS = """
╔═══════════════════════════════════════════════════════════╗
║                    GERENCIAR USUÁRIOS                     ║
╚═══════════════════════════════════════════════════════════╝

  1 - Listar Usuários
  2 - Buscar Usuário (por email)
  3 - Inserir Novo Usuário
  4 - Atualizar Usuário
  5 - Remover Usuário
  6 - Adicionar Classificação de Humor
  7 - Adicionar Histórico de Meditação
  0 - Voltar

"""

MENU_MEDITACOES = """
╔═══════════════════════════════════════════════════════════╗
║                   GERENCIAR MEDITAÇÕES                    ║
╚═══════════════════════════════════════════════════════════╝

  1 - Listar Meditações
  2 - Buscar Meditação (por título)
  3 - Inserir Nova Meditação
  4 - Atualizar Meditação
  5 - Remover Meditação
  6 - Buscar por Categoria
  7 - Buscar por Tipo
  0 - Voltar

"""

# ==================== CATEGORIAS E TIPOS ====================

CATEGORIAS_MEDITACAO = [
    "iniciante",
    "intermediário",
    "avançado"
]

TIPOS_MEDITACAO = [
    "respiração",
    "mindfulness",
    "body scan",
    "visualização",
    "mantra",
    "relaxamento",
    "sono"
]

TIPOS_AVALIACAO = [
    "ansiedade",
    "depressao",
    "estresse",
    "burnout"
]

NIVEIS_HUMOR = {
    1: "Muito Ruim 😢",
    2: "Ruim 😟",
    3: "Neutro 😐",
    4: "Bom 🙂",
    5: "Muito Bom 😊"
}

# ==================== FUNÇÕES AUXILIARES ====================

def exibir_menu(menu):
    """Exibe um menu formatado"""
    print(menu)

def limpar_tela():
    """Limpa a tela"""
    import os
    os.system('clear' if os.name != 'nt' else 'cls')

def pausar():
    """Pausa e aguarda ENTER"""
    input("\nPressione ENTER para continuar...")

def confirmar(mensagem="Confirma operação?"):
    """Solicita confirmação do usuário"""
    resposta = input(f"{mensagem} (s/N): ").strip().lower()
    return resposta == 's' or resposta == 'sim'

def exibir_erro(mensagem):
    """Exibe mensagem de erro formatada"""
    print(f"\n❌ ERRO: {mensagem}\n")

def exibir_sucesso(mensagem):
    """Exibe mensagem de sucesso formatada"""
    print(f"\n✅ SUCESSO: {mensagem}\n")

def exibir_aviso(mensagem):
    """Exibe mensagem de aviso formatada"""
    print(f"\n⚠️  AVISO: {mensagem}\n")
