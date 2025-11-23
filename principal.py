"""
Principal - Sistema Calmou MongoDB
Arquivo principal com interface CLI completa
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.splash_screen import SplashScreen
from src.utils.config import *
from src.reports.relatorios import Relatorios
from src.controller.controller_usuario import ControllerUsuario
from src.controller.controller_meditacao import ControllerMeditacao
from src.model.usuario import Usuario, Endereco, ClassificacaoHumor, HistoricoMeditacao
from src.model.meditacao import Meditacao
from src.conexion.mongo_conexao import fechar_mongo
from bson import ObjectId


class SistemaCalmou:
    """Classe principal do sistema"""

    def __init__(self):
        """Inicializa o sistema"""
        self.controller_usuario = ControllerUsuario()
        self.controller_meditacao = ControllerMeditacao()
        self.relatorios = Relatorios()

    # ==================== MENU PRINCIPAL ====================

    def executar(self):
        """Executa o sistema"""
        # Exibe splash screen
        splash = SplashScreen()
        splash.exibir()

        # Loop principal
        while True:
            limpar_tela()
            exibir_menu(MENU_PRINCIPAL)

            opcao = input("Digite a opção desejada: ").strip()

            if opcao == '1':
                self.relatorios.menu_relatorios()
            elif opcao == '2':
                self.menu_usuarios()
            elif opcao == '3':
                self.menu_meditacoes()
            elif opcao == '0':
                if confirmar("Deseja realmente sair?"):
                    print("\n👋 Obrigado por usar o Sistema Calmou!\n")
                    fechar_mongo()
                    break
            else:
                exibir_erro("Opção inválida!")
                pausar()

    # ==================== MENU USUÁRIOS ====================

    def menu_usuarios(self):
        """Menu de gerenciamento de usuários"""
        while True:
            limpar_tela()
            exibir_menu(MENU_USUARIOS)

            opcao = input("Digite a opção desejada: ").strip()

            if opcao == '1':
                self.listar_usuarios()
            elif opcao == '2':
                self.buscar_usuario_por_email()
            elif opcao == '3':
                self.inserir_usuario()
            elif opcao == '4':
                self.atualizar_usuario()
            elif opcao == '5':
                self.remover_usuario()
            elif opcao == '6':
                self.adicionar_classificacao_humor()
            elif opcao == '7':
                self.adicionar_historico_meditacao()
            elif opcao == '0':
                break
            else:
                exibir_erro("Opção inválida!")
                pausar()

    def listar_usuarios(self):
        """Lista todos os usuários"""
        limpar_tela()
        print("\n" + "=" * 80)
        print("LISTA DE USUÁRIOS".center(80))
        print("=" * 80 + "\n")

        usuarios = self.controller_usuario.listar_resumo()

        if not usuarios:
            exibir_aviso("Nenhum usuário cadastrado")
        else:
            print(f"{'ID':<28} {'NOME':<30} {'EMAIL':<30}")
            print("-" * 90)
            for user in usuarios:
                print(f"{str(user['_id']):<28} {user['nome'][:29]:<30} {user['email'][:29]:<30}")

            print(f"\nTotal: {len(usuarios)} usuário(s)")

        pausar()

    def buscar_usuario_por_email(self):
        """Busca usuário por email"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("BUSCAR USUÁRIO POR EMAIL".center(60))
        print("=" * 60 + "\n")

        email = input("Digite o email do usuário: ").strip()

        usuario = self.controller_usuario.buscar_por_email(email)

        if usuario:
            print(f"\n✅ Usuário encontrado:")
            print(f"  ID: {usuario.get_id()}")
            print(f"  Nome: {usuario.get_nome()}")
            print(f"  Email: {usuario.get_email()}")
            print(f"  CPF: {usuario.get_cpf() or 'N/A'}")
            print(f"  Data Cadastro: {usuario.get_data_cadastro()}")
            print(f"  Classificações de Humor: {len(usuario.get_classificacoes_humor())}")
            print(f"  Histórico de Meditações: {len(usuario.get_historico_meditacoes())}")
        else:
            exibir_aviso(f"Usuário com email '{email}' não encontrado")

        pausar()

    def inserir_usuario(self):
        """Insere novo usuário"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("INSERIR NOVO USUÁRIO".center(60))
        print("=" * 60 + "\n")

        try:
            # Dados obrigatórios
            nome = input("Nome: ").strip()
            email = input("Email: ").strip()
            senha = input("Senha: ").strip()

            if not nome or not email or not senha:
                exibir_erro("Nome, email e senha são obrigatórios!")
                pausar()
                return

            # Hash da senha (simplificado - em produção use bcrypt)
            import hashlib
            password_hash = hashlib.sha256(senha.encode()).hexdigest()

            # Dados opcionais
            cpf = input("CPF (Enter para pular): ").strip() or None
            data_nasc_str = input("Data de Nascimento (dd/mm/aaaa, Enter para pular): ").strip()

            data_nascimento = None
            if data_nasc_str:
                try:
                    data_nascimento = datetime.strptime(data_nasc_str, "%d/%m/%Y")
                except:
                    exibir_aviso("Data inválida, será ignorada")

            tipo_sanguineo = input("Tipo Sanguíneo (Enter para pular): ").strip() or None
            alergias = input("Alergias (Enter para pular): ").strip() or None

            # Cria usuário
            usuario = Usuario(
                nome=nome,
                email=email,
                password_hash=password_hash,
                cpf=cpf,
                data_nascimento=data_nascimento,
                tipo_sanguineo=tipo_sanguineo,
                alergias=alergias
            )

            # Insere
            usuario_id = self.controller_usuario.inserir_usuario(usuario)

            if usuario_id:
                exibir_sucesso(f"Usuário inserido com ID: {usuario_id}")
            else:
                exibir_erro("Falha ao inserir usuário")

        except Exception as e:
            exibir_erro(f"Erro ao inserir usuário: {e}")

        pausar()

    def atualizar_usuario(self):
        """Atualiza usuário"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("ATUALIZAR USUÁRIO".center(60))
        print("=" * 60 + "\n")

        email = input("Digite o email do usuário: ").strip()

        usuario = self.controller_usuario.buscar_por_email(email)

        if not usuario:
            exibir_erro(f"Usuário com email '{email}' não encontrado")
            pausar()
            return

        print(f"\n✅ Usuário encontrado: {usuario.get_nome()}")
        print("\nDeixe em branco para manter o valor atual\n")

        # Campos a atualizar
        novo_nome = input(f"Novo nome [{usuario.get_nome()}]: ").strip()
        novo_email = input(f"Novo email [{usuario.get_email()}]: ").strip()
        novo_tipo_sanguineo = input(f"Novo tipo sanguíneo [{usuario.get_tipo_sanguineo() or 'N/A'}]: ").strip()
        novas_alergias = input(f"Novas alergias [{usuario.get_alergias() or 'N/A'}]: ").strip()

        # Monta dicionário de atualização
        campos_atualizados = {}
        if novo_nome:
            campos_atualizados["nome"] = novo_nome
        if novo_email:
            campos_atualizados["email"] = novo_email
        if novo_tipo_sanguineo:
            campos_atualizados["tipo_sanguineo"] = novo_tipo_sanguineo
        if novas_alergias:
            campos_atualizados["alergias"] = novas_alergias

        if not campos_atualizados:
            exibir_aviso("Nenhum campo foi alterado")
            pausar()
            return

        if confirmar("Confirma atualização?"):
            if self.controller_usuario.atualizar_usuario(usuario.get_id(), campos_atualizados):
                exibir_sucesso("Usuário atualizado com sucesso")
            else:
                exibir_erro("Falha ao atualizar usuário")

        pausar()

    def remover_usuario(self):
        """Remove usuário"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("REMOVER USUÁRIO".center(60))
        print("=" * 60 + "\n")

        email = input("Digite o email do usuário: ").strip()

        usuario = self.controller_usuario.buscar_por_email(email)

        if not usuario:
            exibir_erro(f"Usuário com email '{email}' não encontrado")
            pausar()
            return

        print(f"\n⚠️  Você está prestes a remover o usuário:")
        print(f"  Nome: {usuario.get_nome()}")
        print(f"  Email: {usuario.get_email()}")
        print(f"  Classificações de Humor: {len(usuario.get_classificacoes_humor())}")
        print(f"  Histórico de Meditações: {len(usuario.get_historico_meditacoes())}")

        if confirmar("\n⚠️  ATENÇÃO: Esta ação não pode ser desfeita. Confirma remoção?"):
            if self.controller_usuario.remover_usuario(usuario.get_id()):
                exibir_sucesso("Usuário removido com sucesso")
            else:
                exibir_erro("Falha ao remover usuário")

        pausar()

    def adicionar_classificacao_humor(self):
        """Adiciona classificação de humor a um usuário"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("ADICIONAR CLASSIFICAÇÃO DE HUMOR".center(60))
        print("=" * 60 + "\n")

        email = input("Digite o email do usuário: ").strip()

        usuario = self.controller_usuario.buscar_por_email(email)

        if not usuario:
            exibir_erro(f"Usuário com email '{email}' não encontrado")
            pausar()
            return

        print(f"\n✅ Usuário: {usuario.get_nome()}\n")
        print("Níveis de humor:")
        for nivel, descricao in NIVEIS_HUMOR.items():
            print(f"  {nivel} - {descricao}")

        try:
            nivel = int(input("\nNível de humor (1-5): ").strip())
            if nivel < 1 or nivel > 5:
                exibir_erro("Nível deve estar entre 1 e 5")
                pausar()
                return

            sentimento = input("Sentimento principal: ").strip()
            notas = input("Notas (opcional): ").strip() or None

            classificacao = ClassificacaoHumor(
                nivel_humor=nivel,
                sentimento_principal=sentimento,
                notas=notas
            )

            if self.controller_usuario.adicionar_classificacao_humor(usuario.get_id(), classificacao):
                exibir_sucesso("Classificação de humor adicionada")
            else:
                exibir_erro("Falha ao adicionar classificação")

        except ValueError:
            exibir_erro("Nível inválido")

        pausar()

    def adicionar_historico_meditacao(self):
        """Adiciona histórico de meditação a um usuário"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("ADICIONAR HISTÓRICO DE MEDITAÇÃO".center(60))
        print("=" * 60 + "\n")

        email = input("Digite o email do usuário: ").strip()

        usuario = self.controller_usuario.buscar_por_email(email)

        if not usuario:
            exibir_erro(f"Usuário com email '{email}' não encontrado")
            pausar()
            return

        print(f"\n✅ Usuário: {usuario.get_nome()}\n")

        # Lista meditações disponíveis
        meditacoes = self.controller_meditacao.listar_resumo(20)

        if not meditacoes:
            exibir_aviso("Nenhuma meditação cadastrada")
            pausar()
            return

        print("Meditações disponíveis:\n")
        for i, med in enumerate(meditacoes, 1):
            print(f"  {i}. {med['titulo']} ({med['tipo']}, {med['duracao_minutos']} min)")

        try:
            escolha = int(input("\nEscolha uma meditação (número): ").strip())

            if escolha < 1 or escolha > len(meditacoes):
                exibir_erro("Opção inválida")
                pausar()
                return

            meditacao_id = meditacoes[escolha - 1]['_id']

            duracao_str = input("Duração real em minutos (Enter para usar a duração padrão): ").strip()
            duracao_real = int(duracao_str) if duracao_str else None

            historico = HistoricoMeditacao(
                meditacao_id=meditacao_id,
                duracao_real_minutos=duracao_real
            )

            if self.controller_usuario.adicionar_historico_meditacao(usuario.get_id(), historico):
                exibir_sucesso("Histórico de meditação adicionado")
            else:
                exibir_erro("Falha ao adicionar histórico")

        except ValueError:
            exibir_erro("Valor inválido")

        pausar()

    # ==================== MENU MEDITAÇÕES ====================

    def menu_meditacoes(self):
        """Menu de gerenciamento de meditações"""
        while True:
            limpar_tela()
            exibir_menu(MENU_MEDITACOES)

            opcao = input("Digite a opção desejada: ").strip()

            if opcao == '1':
                self.listar_meditacoes()
            elif opcao == '2':
                self.buscar_meditacao_por_titulo()
            elif opcao == '3':
                self.inserir_meditacao()
            elif opcao == '4':
                self.atualizar_meditacao()
            elif opcao == '5':
                self.remover_meditacao()
            elif opcao == '6':
                self.buscar_meditacao_por_categoria()
            elif opcao == '7':
                self.buscar_meditacao_por_tipo()
            elif opcao == '0':
                break
            else:
                exibir_erro("Opção inválida!")
                pausar()

    def listar_meditacoes(self):
        """Lista todas as meditações"""
        limpar_tela()
        print("\n" + "=" * 90)
        print("LISTA DE MEDITAÇÕES".center(90))
        print("=" * 90 + "\n")

        meditacoes = self.controller_meditacao.listar_resumo()

        if not meditacoes:
            exibir_aviso("Nenhuma meditação cadastrada")
        else:
            print(f"{'TÍTULO':<35} {'TIPO':<20} {'CATEGORIA':<15} {'DURAÇÃO':<10}")
            print("-" * 90)
            for med in meditacoes:
                titulo = med['titulo'][:34]
                tipo = med['tipo'][:19]
                categoria = med['categoria'][:14]
                duracao = f"{med['duracao_minutos']} min"
                print(f"{titulo:<35} {tipo:<20} {categoria:<15} {duracao:<10}")

            print(f"\nTotal: {len(meditacoes)} meditação(ões)")

        pausar()

    def buscar_meditacao_por_titulo(self):
        """Busca meditação por título"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("BUSCAR MEDITAÇÃO POR TÍTULO".center(60))
        print("=" * 60 + "\n")

        titulo = input("Digite o título da meditação: ").strip()

        meditacao = self.controller_meditacao.buscar_por_titulo(titulo)

        if meditacao:
            print(f"\n✅ Meditação encontrada:")
            print(f"  ID: {meditacao.get_id()}")
            print(f"  Título: {meditacao.get_titulo()}")
            print(f"  Descrição: {meditacao.get_descricao()}")
            print(f"  Tipo: {meditacao.get_tipo()}")
            print(f"  Categoria: {meditacao.get_categoria()}")
            print(f"  Duração: {meditacao.get_duracao_minutos()} min")
        else:
            exibir_aviso(f"Meditação '{titulo}' não encontrada")

        pausar()

    def inserir_meditacao(self):
        """Insere nova meditação"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("INSERIR NOVA MEDITAÇÃO".center(60))
        print("=" * 60 + "\n")

        try:
            titulo = input("Título: ").strip()
            descricao = input("Descrição: ").strip()
            duracao = int(input("Duração (minutos): ").strip())
            url_audio = input("URL do áudio (Enter para pular): ").strip() or None

            print("\nTipos disponíveis:")
            for i, tipo in enumerate(TIPOS_MEDITACAO, 1):
                print(f"  {i}. {tipo}")
            tipo_idx = int(input("Escolha o tipo (número): ").strip()) - 1
            tipo = TIPOS_MEDITACAO[tipo_idx]

            print("\nCategorias disponíveis:")
            for i, cat in enumerate(CATEGORIAS_MEDITACAO, 1):
                print(f"  {i}. {cat}")
            cat_idx = int(input("Escolha a categoria (número): ").strip()) - 1
            categoria = CATEGORIAS_MEDITACAO[cat_idx]

            imagem_capa = input("URL da imagem de capa (Enter para pular): ").strip() or None

            meditacao = Meditacao(
                titulo=titulo,
                descricao=descricao,
                duracao_minutos=duracao,
                url_audio=url_audio,
                tipo=tipo,
                categoria=categoria,
                imagem_capa=imagem_capa
            )

            meditacao_id = self.controller_meditacao.inserir_meditacao(meditacao)

            if meditacao_id:
                exibir_sucesso(f"Meditação inserida com ID: {meditacao_id}")
            else:
                exibir_erro("Falha ao inserir meditação")

        except Exception as e:
            exibir_erro(f"Erro ao inserir meditação: {e}")

        pausar()

    def atualizar_meditacao(self):
        """Atualiza meditação"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("ATUALIZAR MEDITAÇÃO".center(60))
        print("=" * 60 + "\n")

        titulo = input("Digite o título da meditação: ").strip()

        meditacao = self.controller_meditacao.buscar_por_titulo(titulo)

        if not meditacao:
            exibir_erro(f"Meditação '{titulo}' não encontrada")
            pausar()
            return

        print(f"\n✅ Meditação encontrada: {meditacao.get_titulo()}")
        print("\nDeixe em branco para manter o valor atual\n")

        novo_titulo = input(f"Novo título [{meditacao.get_titulo()}]: ").strip()
        nova_descricao = input(f"Nova descrição [{meditacao.get_descricao()}]: ").strip()

        campos_atualizados = {}
        if novo_titulo:
            campos_atualizados["titulo"] = novo_titulo
        if nova_descricao:
            campos_atualizados["descricao"] = nova_descricao

        if not campos_atualizados:
            exibir_aviso("Nenhum campo foi alterado")
            pausar()
            return

        if confirmar("Confirma atualização?"):
            if self.controller_meditacao.atualizar_meditacao(meditacao.get_id(), campos_atualizados):
                exibir_sucesso("Meditação atualizada com sucesso")
            else:
                exibir_erro("Falha ao atualizar meditação")

        pausar()

    def remover_meditacao(self):
        """Remove meditação"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("REMOVER MEDITAÇÃO".center(60))
        print("=" * 60 + "\n")

        titulo = input("Digite o título da meditação: ").strip()

        meditacao = self.controller_meditacao.buscar_por_titulo(titulo)

        if not meditacao:
            exibir_erro(f"Meditação '{titulo}' não encontrada")
            pausar()
            return

        print(f"\n⚠️  Você está prestes a remover a meditação:")
        print(f"  Título: {meditacao.get_titulo()}")
        print(f"  Tipo: {meditacao.get_tipo()}")
        print(f"  Duração: {meditacao.get_duracao_minutos()} min")

        # O controller já faz a verificação de referências
        if self.controller_meditacao.remover_meditacao(meditacao.get_id()):
            exibir_sucesso("Meditação removida com sucesso")
        else:
            exibir_erro("Falha ao remover meditação")

        pausar()

    def buscar_meditacao_por_categoria(self):
        """Busca meditações por categoria"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("BUSCAR POR CATEGORIA".center(60))
        print("=" * 60 + "\n")

        print("Categorias disponíveis:")
        for i, cat in enumerate(CATEGORIAS_MEDITACAO, 1):
            print(f"  {i}. {cat}")

        try:
            escolha = int(input("\nEscolha uma categoria (número): ").strip())
            categoria = CATEGORIAS_MEDITACAO[escolha - 1]

            meditacoes = self.controller_meditacao.buscar_por_categoria(categoria)

            if meditacoes:
                print(f"\n✅ Encontradas {len(meditacoes)} meditação(ões):\n")
                for med in meditacoes:
                    print(f"  - {med.get_titulo()} ({med.get_tipo()}, {med.get_duracao_minutos()} min)")
            else:
                exibir_aviso(f"Nenhuma meditação na categoria '{categoria}'")

        except (ValueError, IndexError):
            exibir_erro("Opção inválida")

        pausar()

    def buscar_meditacao_por_tipo(self):
        """Busca meditações por tipo"""
        limpar_tela()
        print("\n" + "=" * 60)
        print("BUSCAR POR TIPO".center(60))
        print("=" * 60 + "\n")

        print("Tipos disponíveis:")
        for i, tipo in enumerate(TIPOS_MEDITACAO, 1):
            print(f"  {i}. {tipo}")

        try:
            escolha = int(input("\nEscolha um tipo (número): ").strip())
            tipo = TIPOS_MEDITACAO[escolha - 1]

            meditacoes = self.controller_meditacao.buscar_por_tipo(tipo)

            if meditacoes:
                print(f"\n✅ Encontradas {len(meditacoes)} meditação(ões):\n")
                for med in meditacoes:
                    print(f"  - {med.get_titulo()} ({med.get_categoria()}, {med.get_duracao_minutos()} min)")
            else:
                exibir_aviso(f"Nenhuma meditação do tipo '{tipo}'")

        except (ValueError, IndexError):
            exibir_erro("Opção inválida")

        pausar()


# ==================== MAIN ====================

if __name__ == "__main__":
    try:
        sistema = SistemaCalmou()
        sistema.executar()
    except KeyboardInterrupt:
        print("\n\n👋 Sistema interrompido pelo usuário. Até logo!\n")
        fechar_mongo()
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}\n")
        import traceback
        traceback.print_exc()
        fechar_mongo()
