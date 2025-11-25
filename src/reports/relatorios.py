"""
Relatórios MongoDB - Calmou API
Implementa relatórios com agregação e lookup (join)
"""

from src.conexion.mongo_conexao import obter_colecao
from datetime import datetime
import os


class Relatorios:
    """Classe para geração de relatórios"""

    def __init__(self):
        """Inicializa os relatórios"""
        self.usuarios_collection = obter_colecao("usuarios")
        self.meditacoes_collection = obter_colecao("meditacoes")

    def limpar_tela(self):
        """Limpa a tela do terminal"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def exibir_cabecalho(self, titulo):
        """Exibe cabeçalho do relatório"""
        print("\n" + "=" * 80)
        print(titulo.center(80))
        print("=" * 80 + "\n")

    # ==================== RELATÓRIO 1: AGREGAÇÃO ====================

    def relatorio_meditacoes_por_categoria_tipo(self):
        """
        RELATÓRIO COM AGREGAÇÃO ($group, $count)
        Total de meditações agrupadas por categoria e tipo
        """
        self.limpar_tela()
        self.exibir_cabecalho("RELATÓRIO: MEDITAÇÕES POR CATEGORIA E TIPO")

        try:
            # Agregação: Agrupa por categoria e tipo, conta total
            pipeline = [
                {
                    "$group": {
                        "_id": {
                            "categoria": "$categoria",
                            "tipo": "$tipo"
                        },
                        "total": {"$sum": 1},
                        "duracao_media": {"$avg": "$duracao_minutos"}
                    }
                },
                {
                    "$sort": {"_id.categoria": 1, "total": -1}
                }
            ]

            resultados = list(self.meditacoes_collection.aggregate(pipeline))

            if not resultados:
                print("⚠️  Nenhuma meditação encontrada\n")
                return

            # Exibe resultados formatados
            print(f"{'CATEGORIA':<20} {'TIPO':<25} {'QUANTIDADE':<15} {'DURAÇÃO MÉDIA':<15}")
            print("-" * 80)

            for item in resultados:
                categoria = item["_id"]["categoria"] or "N/A"
                tipo = item["_id"]["tipo"] or "N/A"
                total = item["total"]
                duracao_media = f"{item['duracao_media']:.1f} min" if item.get("duracao_media") else "N/A"

                print(f"{categoria:<20} {tipo:<25} {total:<15} {duracao_media:<15}")

            # Total geral
            total_geral = sum(item["total"] for item in resultados)
            print("-" * 80)
            print(f"{'TOTAL GERAL:':<20} {'':<25} {total_geral:<15}\n")

        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}\n")

    def relatorio_usuarios_por_humor(self):
        """
        RELATÓRIO COM AGREGAÇÃO ($unwind, $group)
        Distribuição de classificações de humor
        """
        self.limpar_tela()
        self.exibir_cabecalho("RELATÓRIO: DISTRIBUIÇÃO DE CLASSIFICAÇÕES DE HUMOR")

        try:
            # Agregação: Desdobra array de humor e agrupa por sentimento
            pipeline = [
                {"$unwind": "$classificacoes_humor"},
                {
                    "$group": {
                        "_id": {
                            "sentimento": "$classificacoes_humor.sentimento_principal",
                            "nivel": "$classificacoes_humor.nivel_humor"
                        },
                        "total": {"$sum": 1}
                    }
                },
                {"$sort": {"_id.nivel": -1, "total": -1}}
            ]

            resultados = list(self.usuarios_collection.aggregate(pipeline))

            if not resultados:
                print("⚠️  Nenhuma classificação de humor encontrada\n")
                return

            # Exibe resultados
            print(f"{'NÍVEL':<10} {'SENTIMENTO':<25} {'QUANTIDADE':<15}")
            print("-" * 50)

            for item in resultados:
                nivel = item["_id"]["nivel"]
                sentimento = item["_id"]["sentimento"] or "N/A"
                total = item["total"]

                # Emoji baseado no nível
                emoji = ["😢", "😟", "😐", "🙂", "😊"][nivel - 1] if 1 <= nivel <= 5 else "❓"

                print(f"{nivel} {emoji:<8} {sentimento:<25} {total:<15}")

            # Total
            total_geral = sum(item["total"] for item in resultados)
            print("-" * 50)
            print(f"{'TOTAL:':<10} {'':<25} {total_geral:<15}\n")

        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}\n")

    # ==================== RELATÓRIO 2: LOOKUP (JOIN) ====================

    def relatorio_historico_meditacoes_completo(self, limite=50):
        """
        RELATÓRIO COM LOOKUP ($lookup - equivalente a JOIN)
        Histórico de meditações com detalhes da meditação
        """
        self.limpar_tela()
        self.exibir_cabecalho("RELATÓRIO: HISTÓRICO DE MEDITAÇÕES (COM DETALHES)")

        try:
            # Agregação com $lookup para fazer join entre usuários e meditações
            pipeline = [
                # Desdobra o array de histórico
                {"$unwind": "$historico_meditacoes"},

                # Faz lookup (join) com a coleção meditacoes
                {
                    "$lookup": {
                        "from": "meditacoes",
                        "localField": "historico_meditacoes.meditacao_id",
                        "foreignField": "_id",
                        "as": "meditacao_detalhes"
                    }
                },

                # Desdobra o resultado do lookup
                {"$unwind": {"path": "$meditacao_detalhes", "preserveNullAndEmptyArrays": True}},

                # Projeta apenas os campos necessários
                {
                    "$project": {
                        "usuario_nome": "$nome",
                        "usuario_email": "$email",
                        "meditacao_titulo": "$meditacao_detalhes.titulo",
                        "meditacao_tipo": "$meditacao_detalhes.tipo",
                        "meditacao_categoria": "$meditacao_detalhes.categoria",
                        "duracao_esperada": "$meditacao_detalhes.duracao_minutos",
                        "duracao_real": "$historico_meditacoes.duracao_real_minutos",
                        "data_conclusao": "$historico_meditacoes.data_conclusao"
                    }
                },

                # Ordena por data mais recente
                {"$sort": {"data_conclusao": -1}},

                # Limita resultados
                {"$limit": limite}
            ]

            resultados = list(self.usuarios_collection.aggregate(pipeline))

            if not resultados:
                print("⚠️  Nenhum histórico de meditação encontrado\n")
                return

            # Exibe resultados
            print(f"{'USUÁRIO':<25} {'MEDITAÇÃO':<30} {'TIPO':<15} {'DATA':<12}")
            print("-" * 90)

            for item in resultados:
                usuario = item.get("usuario_nome", "N/A")[:24]
                meditacao = item.get("meditacao_titulo", "Meditação Removida")[:29]
                tipo = item.get("meditacao_tipo", "N/A")[:14]
                data = item.get("data_conclusao", "N/A")

                if isinstance(data, datetime):
                    data_str = data.strftime("%d/%m/%Y")
                else:
                    data_str = "N/A"

                print(f"{usuario:<25} {meditacao:<30} {tipo:<15} {data_str:<12}")

            print("-" * 90)
            print(f"Total de registros: {len(resultados)}\n")

        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}\n")
            import traceback
            traceback.print_exc()

    def relatorio_usuarios_mais_ativos(self, limite=10):
        """
        RELATÓRIO COM AGREGAÇÃO E LOOKUP
        Usuários mais ativos (mais meditações concluídas)
        """
        self.limpar_tela()
        self.exibir_cabecalho(f"RELATÓRIO: TOP {limite} USUÁRIOS MAIS ATIVOS")

        try:
            pipeline = [
                # Projeta apenas nome, email e tamanho do array de histórico
                {
                    "$project": {
                        "nome": 1,
                        "email": 1,
                        "total_meditacoes": {"$size": {"$ifNull": ["$historico_meditacoes", []]}},
                        "total_humores": {"$size": {"$ifNull": ["$classificacoes_humor", []]}},
                        "data_cadastro": 1
                    }
                },

                # Ordena por total de meditações
                {"$sort": {"total_meditacoes": -1}},

                # Limita ao top N
                {"$limit": limite}
            ]

            resultados = list(self.usuarios_collection.aggregate(pipeline))

            if not resultados:
                print("⚠️  Nenhum usuário encontrado\n")
                return

            # Exibe resultados
            print(f"{'#':<5} {'NOME':<30} {'MEDITAÇÕES':<15} {'HUMORES':<15}")
            print("-" * 70)

            for i, item in enumerate(resultados, 1):
                nome = item.get("nome", "N/A")[:29]
                total_med = item.get("total_meditacoes", 0)
                total_humor = item.get("total_humores", 0)

                # Emoji baseado na posição
                emoji = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else "  "

                print(f"{emoji} {i:<3} {nome:<30} {total_med:<15} {total_humor:<15}")

            print("-" * 70 + "\n")

        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}\n")

    # ==================== MENU DE RELATÓRIOS ====================

    def menu_relatorios(self):
        """Exibe menu de relatórios"""
        while True:
            self.limpar_tela()
            print("\n" + "=" * 60)
            print("MENU DE RELATÓRIOS".center(60))
            print("=" * 60 + "\n")

            print("Escolha um relatório:\n")
            print("  1 - Meditações por Categoria e Tipo (AGREGAÇÃO)")
            print("  2 - Distribuição de Classificações de Humor (AGREGAÇÃO)")
            print("  3 - Histórico de Meditações Completo (LOOKUP/JOIN)")
            print("  4 - Top 10 Usuários Mais Ativos (AGREGAÇÃO + CÁLCULO)")
            print("  0 - Voltar ao Menu Principal\n")

            opcao = input("Digite a opção desejada: ").strip()

            if opcao == '1':
                self.relatorio_meditacoes_por_categoria_tipo()
                input("\nPressione ENTER para continuar...")
            elif opcao == '2':
                self.relatorio_usuarios_por_humor()
                input("\nPressione ENTER para continuar...")
            elif opcao == '3':
                self.relatorio_historico_meditacoes_completo()
                input("\nPressione ENTER para continuar...")
            elif opcao == '4':
                self.relatorio_usuarios_mais_ativos()
                input("\nPressione ENTER para continuar...")
            elif opcao == '0':
                break
            else:
                print("\n❌ Opção inválida!")
                input("Pressione ENTER para continuar...")


# ==================== TESTE ====================

if __name__ == "__main__":
    """Teste dos relatórios"""
    relatorios = Relatorios()
    relatorios.menu_relatorios()
