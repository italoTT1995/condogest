import sqlalchemy
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

def migrate():
    with app.app_context():
        print("--- Iniciando Migração de Banco de Dados (Produção) ---")
        engine = db.engine
        inspector = inspect(engine)
        
        # 1. Garantir que todas as tabelas novas existam
        print("Verificando/Criando novas tabelas...")
        db.create_all()
        
        # Helper para adicionar colunas se não existirem
        def add_column(table_name, column_name, column_type):
            try:
                columns = [c['name'] for c in inspector.get_columns(table_name)]
                if column_name not in columns:
                    print(f"Adicionando coluna '{column_name}' à tabela '{table_name}'...")
                    with engine.connect() as conn:
                        # "user" é palavra reservada no Postgres, precisa de aspas
                        quoted_table = f'"{table_name}"' if table_name.lower() == 'user' else table_name
                        conn.execute(text(f"ALTER TABLE {quoted_table} ADD COLUMN {column_name} {column_type}"))
                        conn.commit()
                        print(f"Coluna '{column_name}' adicionada com sucesso.")
                else:
                    # print(f"Coluna '{column_name}' já existe na tabela '{table_name}'.")
                    pass
            except Exception as e:
                print(f"Nota ao processar '{column_name}' em '{table_name}': {e}")

        # 2. Atualizar tabela 'user' com colunas de segurança e novas funções
        add_column('user', 'profile_image', "VARCHAR(255) DEFAULT 'default.jpg'")
        add_column('user', 'role_id', 'INTEGER REFERENCES role(id)')
        add_column('user', 'failed_login_attempts', 'INTEGER DEFAULT 0')
        add_column('user', 'locked_until', 'TIMESTAMP')
        add_column('user', 'must_change_password', 'BOOLEAN DEFAULT FALSE')
        add_column('user', 'condo_id', 'INTEGER REFERENCES condominium(id)')
        add_column('user', 'access_token', 'VARCHAR(100)')
        
        # 3. Atualizar tabela 'notice' (Avisos)
        add_column('notice', 'image_filename', 'VARCHAR(255)')
        add_column('notice', 'is_important', 'BOOLEAN DEFAULT FALSE')
        add_column('notice', 'condo_id', 'INTEGER REFERENCES condominium(id)')
        add_column('notice', 'created_by', 'INTEGER REFERENCES "user"(id)')
        add_column('notice', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # 4. Atualizar tabela 'payment' e 'expense' (Financeiro)
        add_column('payment', 'unit_id', 'INTEGER REFERENCES unit(id)')
        add_column('payment', 'condo_id', 'INTEGER REFERENCES condominium(id)')
        add_column('payment', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        add_column('expense', 'proof_filename', 'VARCHAR(255)')
        add_column('expense', 'condo_id', 'INTEGER REFERENCES condominium(id)')
        add_column('expense', 'created_by', 'INTEGER REFERENCES "user"(id)')
        add_column('expense', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # 5. Atualizar tabela 'unit'
        add_column('unit', 'condo_id', 'INTEGER REFERENCES condominium(id)')
        
        # 6. Atualizar tabela 'ticket' (Chamados/Denúncias)
        add_column('ticket', 'category', "VARCHAR(20) DEFAULT 'maintenance'")
        add_column('ticket', 'image_filename', 'VARCHAR(255)')
        
        # 7. Atualizar outras tabelas
        add_column('reservation', 'access_token', 'VARCHAR(100)')
        add_column('common_area', 'condo_id', 'INTEGER REFERENCES condominium(id)')

        # 8. Garantir Roles básicas se não existirem
        from app.models.user import Role
        roles = [
            {'name': 'Admin', 'description': 'Acesso total', 'is_admin': True, 'can_manage_concierge': True, 'can_manage_reservations': True, 'can_manage_complaints': True},
            {'name': 'Síndico', 'description': 'Gestão do condomínio', 'is_admin': True, 'can_manage_concierge': True, 'can_manage_reservations': True, 'can_manage_complaints': True},
            {'name': 'Porteiro', 'description': 'Portaria e encomendas', 'is_admin': False, 'can_manage_concierge': True, 'can_manage_reservations': False, 'can_manage_complaints': False},
            {'name': 'Morador', 'description': 'Acesso de residente', 'is_admin': False, 'can_manage_concierge': False, 'can_manage_reservations': False, 'can_manage_complaints': False}
        ]
        
        for r_data in roles:
            role = Role.query.filter_by(name=r_data['name']).first()
            if not role:
                print(f"Criando Role: {r_data['name']}")
                role = Role(**r_data)
                db.session.add(role)
        
        db.session.commit()
        print("--- Migração Concluída com Sucesso ---")

if __name__ == "__main__":
    migrate()
