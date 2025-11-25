"""
API Calmou - Backend Flask com MongoDB
Aplicação de saúde mental e bem-estar
"""
import logging
import os
from datetime import timedelta, datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import ValidationError
import bcrypt
from bson import ObjectId

# Imports do projeto MongoDB
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conexion.mongo_conexao import conectar_mongo, fechar_mongo
from src.controller.controller_usuario import ControllerUsuario
from src.controller.controller_meditacao import ControllerMeditacao
from src.model.usuario import Usuario, ClassificacaoHumor, HistoricoMeditacao
from src.model.meditacao import Meditacao

# ==================== CONFIGURAÇÃO DO APP ====================

app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'calmou-secret-key-dev-2024')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'calmou-jwt-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# ==================== LOGGING ====================

os.makedirs('logs', exist_ok=True)

formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

file_handler = RotatingFileHandler(
    'logs/api.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)

# ==================== EXTENSÕES ====================

# CORS
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Em produção, especificar origens
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# JWT
jwt = JWTManager(app)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://"
)

# Controllers
db = conectar_mongo()
controller_usuario = ControllerUsuario()
controller_meditacao = ControllerMeditacao()

# ==================== ERROR HANDLERS ====================

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    app.logger.warning(f"Erro de validação: {error.messages}")
    return jsonify({
        'mensagem': 'Erro de validação',
        'erros': error.messages
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'mensagem': 'Recurso não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Erro interno: {error}")
    return jsonify({'mensagem': 'Erro interno do servidor'}), 500

@app.errorhandler(429)
def ratelimit_handler(error):
    app.logger.warning(f"Rate limit atingido: {get_remote_address()}")
    return jsonify({
        'mensagem': 'Muitas requisições. Tente novamente mais tarde.'
    }), 429

# ==================== JWT CALLBACKS ====================

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'mensagem': 'Token expirado',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'mensagem': 'Token inválido',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'mensagem': 'Token de autenticação não fornecido',
        'error': 'authorization_required'
    }), 401

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def serialize_objectid(obj):
    """Converte ObjectId para string em objetos"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: serialize_objectid(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_objectid(item) for item in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# ==================== ROTAS PÚBLICAS ====================

@app.route('/', methods=['GET'])
def index():
    """Rota raiz - Informações da API"""
    return jsonify({
        'app': 'Calmou API MongoDB',
        'version': '2.0.0',
        'status': 'online',
        'database': 'MongoDB',
        'endpoints': {
            'auth': '/login, /register, /refresh',
            'users': '/usuarios, /perfil',
            'mood': '/humor, /humor/relatorio-semanal',
            'meditations': '/meditacoes, /meditacoes/<id>',
            'meditation_history': '/meditacoes/historico, /meditacoes/estatisticas',
            'assessments': '/avaliacoes, /avaliacoes/historico',
            'stats': '/stats'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoramento"""
    try:
        # Testa conexão com MongoDB
        db.command('ping')
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        app.logger.error(f"Health check falhou: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected'
        }), 503

# ==================== AUTENTICAÇÃO ====================

@app.route('/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    """Endpoint de registro de novo usuário"""
    try:
        dados = request.get_json()

        if not dados or not dados.get('nome') or not dados.get('email') or not dados.get('password'):
            return jsonify({"mensagem": "Nome, email e senha são obrigatórios"}), 400

        # Verifica se email já existe
        existing_user = controller_usuario.buscar_por_email(dados['email'])
        if existing_user:
            return jsonify({"mensagem": "Email já cadastrado"}), 409

        # Cria usuário
        password_hash = hash_password(dados['password'])

        new_user = Usuario(
            nome=dados['nome'],
            email=dados['email'],
            password_hash=password_hash,
            cpf=dados.get('cpf'),
            data_nascimento=dados.get('data_nascimento'),
            tipo_sanguineo=dados.get('tipo_sanguineo'),
            alergias=dados.get('alergias'),
            foto_perfil=dados.get('foto_perfil')
        )

        user_id = controller_usuario.inserir_usuario(new_user)

        if not user_id:
            return jsonify({"mensagem": "Erro ao criar usuário"}), 500

        # Cria tokens
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))

        app.logger.info(f"Novo usuário registrado: {dados['email']}")

        return jsonify({
            "mensagem": "Usuário criado com sucesso!",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "usuario": {
                "id": str(user_id),
                "nome": dados['nome'],
                "email": dados['email']
            }
        }), 201

    except Exception as e:
        app.logger.error(f"Erro ao criar usuário: {str(e)}")
        return jsonify({"mensagem": f"Erro ao criar usuário: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Endpoint de login com JWT"""
    try:
        dados = request.get_json()

        if not dados or not dados.get('email') or not dados.get('password'):
            return jsonify({"mensagem": "Email e senha são obrigatórios"}), 400

        email = dados['email']
        password = dados['password']

        # Busca usuário
        user_found = controller_usuario.buscar_por_email(email)

        if not user_found:
            app.logger.warning(f"Tentativa de login com email inexistente: {email}")
            return jsonify({"mensagem": "Credenciais inválidas"}), 401

        # Verifica senha
        if not verify_password(password, user_found.get_password_hash()):
            app.logger.warning(f"Tentativa de login com senha incorreta: {email}")
            return jsonify({"mensagem": "Credenciais inválidas"}), 401

        # Cria tokens JWT
        user_id = str(user_found.get_id())
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        app.logger.info(f"Login bem-sucedido: {email}")

        return jsonify({
            "mensagem": "Login bem-sucedido!",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "usuario": {
                "id": user_id,
                "nome": user_found.get_nome(),
                "email": user_found.get_email()
            }
        }), 200

    except Exception as e:
        app.logger.error(f"Erro no login: {str(e)}")
        return jsonify({"mensagem": "Erro ao realizar login"}), 500

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Endpoint para renovar access token"""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)

        return jsonify({
            'access_token': new_access_token
        }), 200

    except Exception as e:
        app.logger.error(f"Erro ao renovar token: {str(e)}")
        return jsonify({'mensagem': 'Erro ao renovar token'}), 500

# ==================== USUÁRIOS ====================

@app.route('/usuarios/<user_id>', methods=['GET'])
@jwt_required()
def obter_usuario(user_id):
    """Retorna dados do usuário"""
    try:
        current_user_id = get_jwt_identity()

        # Verifica se está acessando o próprio perfil
        if current_user_id != user_id:
            return jsonify({"mensagem": "Acesso não autorizado"}), 403

        # Busca usuário no MongoDB
        usuario = db.usuarios.find_one({"_id": ObjectId(user_id)})

        if not usuario:
            return jsonify({"mensagem": "Usuário não encontrado"}), 404

        # Remove campos sensíveis
        usuario_data = {
            'id': str(usuario['_id']),
            'nome': usuario.get('nome'),
            'email': usuario.get('email'),
            'data_cadastro': usuario.get('data_cadastro').isoformat() if usuario.get('data_cadastro') else None
        }

        return jsonify(usuario_data), 200

    except Exception as e:
        app.logger.error(f"Erro ao buscar usuário: {str(e)}")
        return jsonify({"mensagem": "Erro ao buscar usuário"}), 500

@app.route('/usuarios/<user_id>/excluir-conta', methods=['DELETE'])
@jwt_required()
def excluir_conta(user_id):
    """Exclui a conta do usuário (todos os dados)"""
    try:
        current_user_id = get_jwt_identity()

        # Verifica se está excluindo a própria conta
        if current_user_id != user_id:
            return jsonify({"mensagem": "Acesso não autorizado"}), 403

        # Exclui o usuário do MongoDB
        resultado = db.usuarios.delete_one({"_id": ObjectId(user_id)})

        if resultado.deleted_count > 0:
            app.logger.info(f"Conta excluída: {user_id}")
            return jsonify({"mensagem": "Conta excluída com sucesso"}), 200
        else:
            return jsonify({"mensagem": "Usuário não encontrado"}), 404

    except Exception as e:
        app.logger.error(f"Erro ao excluir conta: {str(e)}")
        return jsonify({"mensagem": "Erro ao excluir conta"}), 500

# ==================== MEDITAÇÕES ====================

@app.route('/meditacoes', methods=['GET'])
def listar_meditacoes():
    """Lista todas as meditações (público)"""
    try:
        meditacoes = controller_meditacao.listar_todas()

        meditacoes_json = []
        for med in meditacoes:
            meditacoes_json.append({
                'id': str(med.get_id()),
                'titulo': med.get_titulo(),
                'descricao': med.get_descricao(),
                'duracao_minutos': med.get_duracao_minutos(),
                'url_audio': med.get_url_audio(),
                'tipo': med.get_tipo(),
                'categoria': med.get_categoria(),
                'imagem_capa': med.get_imagem_capa()
            })

        return jsonify(meditacoes_json), 200

    except Exception as e:
        app.logger.error(f"Erro ao listar meditações: {str(e)}")
        return jsonify({"mensagem": "Erro ao listar meditações"}), 500

@app.route('/meditacoes/<meditacao_id>', methods=['GET'])
def buscar_meditacao(meditacao_id):
    """Busca detalhes de uma meditação específica"""
    try:
        from bson import ObjectId
        meditacao = controller_meditacao.buscar_por_id(ObjectId(meditacao_id))

        if not meditacao:
            return jsonify({"mensagem": "Meditação não encontrada"}), 404

        return jsonify({
            'id': str(meditacao.get_id()),
            'titulo': meditacao.get_titulo(),
            'descricao': meditacao.get_descricao(),
            'duracao_minutos': meditacao.get_duracao_minutos(),
            'url_audio': meditacao.get_url_audio(),
            'tipo': meditacao.get_tipo(),
            'categoria': meditacao.get_categoria(),
            'imagem_capa': meditacao.get_imagem_capa()
        }), 200

    except Exception as e:
        app.logger.error(f"Erro ao buscar meditação: {str(e)}")
        return jsonify({"mensagem": "Erro ao buscar meditação"}), 500

# ==================== PERFIL USUÁRIO ====================

@app.route('/perfil', methods=['GET'])
@jwt_required()
def get_perfil():
    """Retorna perfil do usuário autenticado"""
    try:
        current_user_id = get_jwt_identity()
        usuario = controller_usuario.buscar_por_id(ObjectId(current_user_id))

        if not usuario:
            return jsonify({"mensagem": "Usuário não encontrado"}), 404

        return jsonify({
            'id': str(usuario.get_id()),
            'nome': usuario.get_nome(),
            'email': usuario.get_email(),
            'cpf': usuario.get_cpf(),
            'data_nascimento': usuario.get_data_nascimento().isoformat() if usuario.get_data_nascimento() else None,
            'tipo_sanguineo': usuario.get_tipo_sanguineo(),
            'alergias': usuario.get_alergias(),
            'foto_perfil': usuario.get_foto_perfil(),
            'data_cadastro': usuario.get_data_cadastro().isoformat() if usuario.get_data_cadastro() else None
        }), 200

    except Exception as e:
        app.logger.error(f"Erro ao buscar perfil: {str(e)}")
        return jsonify({"mensagem": "Erro ao buscar perfil"}), 500

@app.route('/perfil', methods=['PUT'])
@jwt_required()
def atualizar_perfil():
    """Atualiza perfil do usuário autenticado"""
    try:
        current_user_id = get_jwt_identity()
        dados = request.get_json()

        if not dados:
            return jsonify({"mensagem": "Nenhum dado fornecido"}), 400

        campos_atualizados = {}

        if 'nome' in dados:
            campos_atualizados['nome'] = dados['nome']
        if 'cpf' in dados:
            campos_atualizados['cpf'] = dados['cpf']
        if 'data_nascimento' in dados:
            campos_atualizados['data_nascimento'] = dados['data_nascimento']
        if 'tipo_sanguineo' in dados:
            campos_atualizados['tipo_sanguineo'] = dados['tipo_sanguineo']
        if 'alergias' in dados:
            campos_atualizados['alergias'] = dados['alergias']
        if 'foto_perfil' in dados:
            campos_atualizados['foto_perfil'] = dados['foto_perfil']

        if not campos_atualizados:
            return jsonify({"mensagem": "Nenhum campo válido para atualizar"}), 400

        resultado = controller_usuario.atualizar_usuario(ObjectId(current_user_id), campos_atualizados)

        if resultado:
            app.logger.info(f"Perfil do usuário {current_user_id} atualizado")
            return jsonify({"mensagem": "Perfil atualizado com sucesso!"}), 200
        else:
            return jsonify({"mensagem": "Erro ao atualizar perfil"}), 500

    except Exception as e:
        app.logger.error(f"Erro ao atualizar perfil: {str(e)}")
        return jsonify({"mensagem": f"Erro ao atualizar perfil: {str(e)}"}), 500

# ==================== HUMOR ====================

@app.route('/humor', methods=['POST'])
@jwt_required()
def registrar_humor():
    """Registra classificação de humor"""
    try:
        current_user_id = get_jwt_identity()
        dados = request.get_json()

        if not dados or 'nivel_humor' not in dados:
            return jsonify({"mensagem": "Nível de humor é obrigatório"}), 400

        classificacao = ClassificacaoHumor(
            nivel_humor=dados['nivel_humor'],
            sentimento_principal=dados.get('sentimento_principal'),
            notas=dados.get('notas')
        )

        resultado = controller_usuario.adicionar_classificacao_humor(
            ObjectId(current_user_id),
            classificacao
        )

        if resultado:
            app.logger.info(f"Humor registrado para usuário {current_user_id}")
            return jsonify({"mensagem": "Registro de humor salvo com sucesso!"}), 201
        else:
            return jsonify({"mensagem": "Erro ao salvar humor"}), 500

    except Exception as e:
        app.logger.error(f"Erro ao salvar humor: {str(e)}")
        return jsonify({"mensagem": "Erro ao salvar humor"}), 500

@app.route('/humor/relatorio-semanal', methods=['GET'])
@jwt_required()
def relatorio_humor_semanal():
    """Retorna relatório semanal de humor do usuário"""
    try:
        current_user_id = get_jwt_identity()

        # Busca usuário e suas classificações de humor
        usuario = controller_usuario.buscar_por_id(ObjectId(current_user_id))

        if not usuario:
            return jsonify({"mensagem": "Usuário não encontrado"}), 404

        # Pega classificações dos últimos 7 dias
        from datetime import datetime, timedelta
        data_limite = datetime.now() - timedelta(days=7)

        classificacoes = usuario.get_classificacoes_humor()

        # Filtra últimos 7 dias
        classificacoes_semana = [
            c for c in classificacoes
            if c.get('data_classificacao') and c['data_classificacao'] >= data_limite
        ]

        # Calcula estatísticas
        if classificacoes_semana:
            niveis = [c.get('nivel_humor', 0) for c in classificacoes_semana]
            media_humor = sum(niveis) / len(niveis) if niveis else 0

            # Conta sentimentos
            sentimentos = {}
            for c in classificacoes_semana:
                sent = c.get('sentimento_principal', 'Não especificado')
                sentimentos[sent] = sentimentos.get(sent, 0) + 1
        else:
            media_humor = 0
            sentimentos = {}

        relatorio = {
            'total_registros': len(classificacoes_semana),
            'media_humor': round(media_humor, 2),
            'sentimentos_frequentes': sentimentos,
            'periodo': '7 dias',
            'registros': [
                {
                    'nivel_humor': c.get('nivel_humor'),
                    'sentimento_principal': c.get('sentimento_principal'),
                    'notas': c.get('notas'),
                    'data': c.get('data_classificacao').isoformat() if c.get('data_classificacao') else None
                }
                for c in sorted(classificacoes_semana, key=lambda x: x.get('data_classificacao', datetime.min), reverse=True)[:7]
            ]
        }

        return jsonify(relatorio), 200

    except Exception as e:
        app.logger.error(f"Erro ao gerar relatório de humor: {str(e)}")
        return jsonify({"mensagem": "Erro ao gerar relatório"}), 500

# ==================== HISTÓRICO MEDITAÇÕES ====================

@app.route('/meditacoes/historico', methods=['POST'])
@jwt_required()
def registrar_meditacao_historico():
    """Registra uma meditação concluída"""
    try:
        current_user_id = get_jwt_identity()
        dados = request.get_json()

        if not dados or 'meditacao_id' not in dados:
            return jsonify({"mensagem": "ID da meditação é obrigatório"}), 400

        historico = HistoricoMeditacao(
            meditacao_id=ObjectId(dados['meditacao_id']),
            duracao_real_minutos=dados.get('duracao_real_minutos')
        )

        resultado = controller_usuario.adicionar_historico_meditacao(
            ObjectId(current_user_id),
            historico
        )

        if resultado:
            app.logger.info(f"Meditação registrada no histórico para usuário {current_user_id}")
            return jsonify({"mensagem": "Meditação registrada com sucesso!"}), 201
        else:
            return jsonify({"mensagem": "Erro ao registrar meditação"}), 500

    except Exception as e:
        app.logger.error(f"Erro ao registrar meditação: {str(e)}")
        return jsonify({"mensagem": "Erro ao registrar meditação"}), 500

# ==================== AVALIAÇÕES ====================

@app.route('/avaliacoes', methods=['POST'])
@jwt_required()
def salvar_avaliacao():
    """Salva resultado de avaliação do usuário autenticado"""
    try:
        current_user_id = get_jwt_identity()
        dados = request.get_json()

        if not dados or 'tipo' not in dados or 'resultado_score' not in dados:
            return jsonify({"mensagem": "Tipo e resultado_score são obrigatórios"}), 400

        # Mapeia tipos do frontend para valores do schema MongoDB
        tipo_mapping = {
            "Avaliação de Ansiedade": "ansiedade",
            "Avaliação de Depressão": "depressao",
            "Avaliação de Estresse": "estresse",
            "Avaliação de Burnout": "burnout",
            "Questionário de Burnout": "burnout",
            "Questionário de Ansiedade": "ansiedade",
            "Questionário de Depressão": "depressao",
            "Questionário de Estresse": "estresse"
        }

        tipo_original = dados.get('tipo', '')
        tipo_normalizado = tipo_mapping.get(tipo_original)

        # Se não encontrou no mapeamento, tenta extrair a palavra-chave
        if not tipo_normalizado:
            tipo_lower = tipo_original.lower()
            if 'ansiedade' in tipo_lower:
                tipo_normalizado = 'ansiedade'
            elif 'depressao' in tipo_lower or 'depressão' in tipo_lower:
                tipo_normalizado = 'depressao'
            elif 'estresse' in tipo_lower:
                tipo_normalizado = 'estresse'
            elif 'burnout' in tipo_lower:
                tipo_normalizado = 'burnout'
            else:
                tipo_normalizado = tipo_lower

        app.logger.info(f"Tipo recebido: '{tipo_original}' -> Normalizado: '{tipo_normalizado}'")

        # Adiciona avaliação no documento do usuário
        avaliacao = {
            "tipo": tipo_normalizado,
            "respostas": dados.get('respostas', {}),
            "resultado_score": dados['resultado_score'],
            "resultado_texto": dados.get('resultado_texto'),
            "data_avaliacao": datetime.now()
        }

        resultado = db.usuarios.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$push": {"resultados_avaliacoes": avaliacao}}
        )

        if resultado.modified_count > 0:
            app.logger.info(f"Avaliação salva para usuário {current_user_id}")
            return jsonify({"mensagem": "Avaliação salva com sucesso!"}), 201
        else:
            return jsonify({"mensagem": "Erro ao salvar avaliação"}), 500

    except Exception as e:
        app.logger.error(f"Erro ao salvar avaliação: {str(e)}")
        return jsonify({"mensagem": f"Erro ao salvar avaliação: {str(e)}"}), 500

@app.route('/avaliacoes/historico', methods=['GET'])
@jwt_required()
def historico_avaliacoes():
    """Retorna histórico de avaliações do usuário autenticado"""
    try:
        current_user_id = get_jwt_identity()

        # Busca usuário diretamente do MongoDB
        usuario = db.usuarios.find_one({"_id": ObjectId(current_user_id)})

        if not usuario:
            return jsonify({"mensagem": "Usuário não encontrado"}), 404

        # Pega avaliações do documento do usuário
        avaliacoes_raw = usuario.get('resultados_avaliacoes', [])

        app.logger.info(f"Usuário {current_user_id} tem {len(avaliacoes_raw)} avaliações no banco")

        # Formata avaliações
        avaliacoes = []
        for av in avaliacoes_raw:
            avaliacoes.append({
                'tipo': av.get('tipo'),
                'respostas': av.get('respostas', {}),
                'resultado_score': av.get('resultado_score'),
                'resultado_texto': av.get('resultado_texto'),
                'data_avaliacao': av.get('data_avaliacao').isoformat() if av.get('data_avaliacao') else None
            })

        # Ordena por data (mais recentes primeiro)
        avaliacoes.sort(key=lambda x: x.get('data_avaliacao', ''), reverse=True)

        app.logger.info(f"Retornando {len(avaliacoes)} avaliações formatadas")

        return jsonify({
            'total': len(avaliacoes),
            'avaliacoes': avaliacoes
        }), 200

    except Exception as e:
        app.logger.error(f"Erro ao buscar histórico de avaliações: {str(e)}")
        return jsonify({"mensagem": "Erro ao buscar histórico"}), 500

# ==================== ESTATÍSTICAS ====================

@app.route('/stats', methods=['GET'])
def obter_estatisticas():
    """Retorna estatísticas gerais do sistema"""
    try:
        stats = {
            'total_usuarios': db.usuarios.count_documents({}),
            'total_meditacoes': db.meditacoes.count_documents({}),
            'database': 'MongoDB',
            'version': '2.0.0'
        }

        return jsonify(stats), 200

    except Exception as e:
        app.logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({"mensagem": "Erro ao buscar estatísticas"}), 500

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    app.logger.info(f"🚀 Iniciando Calmou API MongoDB v2.0.0")
    app.logger.info(f"🗄️ Database: MongoDB")
    app.logger.info(f"🌍 Ambiente: development")

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
