// Script de inicialização do MongoDB
// Executado automaticamente quando o container é criado pela primeira vez

// Criar banco de dados
db = db.getSiblingDB('calmou_db');

// Criar usuário específico para a aplicação
db.createUser({
  user: 'calmou_app',
  pwd: 'calmou_app_2024',
  roles: [
    {
      role: 'readWrite',
      db: 'calmou_db'
    }
  ]
});

print('✅ Banco de dados calmou_db criado');
print('✅ Usuário calmou_app criado com permissões readWrite');

// Criar coleções básicas (os índices serão criados pelo script Python)
db.createCollection('usuarios');
db.createCollection('meditacoes');

print('✅ Coleções usuarios e meditacoes criadas');
print('🚀 MongoDB inicializado com sucesso!');
