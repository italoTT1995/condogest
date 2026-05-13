import os
import logging
from app import db
from app.models.user import User, Role

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista de usuários protegidos pelo sistema
PROTECTED_USERS = {
    'admin_sistema': {
        'label': 'ADMIN',
        'email_env': 'ADMIN_EMAIL',
        'default_email': 'admin@system.com',
        'pass_env': 'ADMIN_PASSWORD',
        'default_pass': 'admin123',
        'role_name': 'Admin',
        'legacy_role': 'admin',
        'role_kwargs': {'is_admin': True, 'can_manage_concierge': True, 'can_manage_reservations': True, 'can_manage_complaints': True}
    },
    'sindico_padrao': {
        'label': 'SINDICO',
        'email_env': 'SINDICO_EMAIL',
        'default_email': 'sindico@system.com',
        'pass_env': 'SINDICO_PASSWORD',
        'default_pass': 'sindico123',
        'role_name': 'Síndico',
        'legacy_role': 'admin',
        'role_kwargs': {'is_admin': True, 'can_manage_concierge': True, 'can_manage_reservations': True, 'can_manage_complaints': True}
    },
    'porteiro_padrao': {
        'label': 'PORTEIRO',
        'email_env': 'PORTEIRO_EMAIL',
        'default_email': 'porteiro@system.com',
        'pass_env': 'PORTEIRO_PASSWORD',
        'default_pass': 'porteiro123',
        'role_name': 'Porteiro',
        'legacy_role': 'porteiro',
        'role_kwargs': {'is_admin': False, 'can_manage_concierge': True, 'can_manage_reservations': False, 'can_manage_complaints': False}
    },
    'morador_padrao': {
        'label': 'MORADOR',
        'email_env': 'MORADOR_EMAIL',
        'default_email': 'morador@system.com',
        'pass_env': 'MORADOR_PASSWORD',
        'default_pass': 'morador123',
        'role_name': 'Morador',
        'legacy_role': 'resident',
        'role_kwargs': {'is_admin': False, 'can_manage_concierge': False, 'can_manage_reservations': False, 'can_manage_complaints': False}
    }
}

def get_or_create_role(name, **kwargs):
    role = Role.query.filter_by(name=name).first()
    if not role:
        role = Role(name=name, **kwargs)
        db.session.add(role)
        db.session.commit()
    else:
        changed = False
        for k, v in kwargs.items():
            if getattr(role, k) != v:
                setattr(role, k, v)
                changed = True
        if changed:
            db.session.commit()
    return role

def seed_default_users():
    logger.info("=== INICIANDO VERIFICAÇÃO DE USUÁRIOS PADRÃO ===")
    
    generated_credentials = []

    for username, data in PROTECTED_USERS.items():
        role = get_or_create_role(data['role_name'], **data['role_kwargs'])
        
        email = os.environ.get(data['email_env'], data['default_email'])
        password = os.environ.get(data['pass_env'], data['default_pass'])
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # Tentar achar pelo email para evitar duplicação de emails únicos
            user_by_email = User.query.filter_by(email=email).first()
            if user_by_email:
                logger.warning(f"Email {email} já em uso por outro usuário. Ajustando email padrão.")
                email = f"padrao_{email}"
                
            user = User(
                username=username,
                email=email,
                role=data['legacy_role'],
                role_id=role.id,
                full_name=f"Usuário Padrão {data['label']}"
            )
            user.set_password(password)
            db.session.add(user)
            logger.info(f"Usuário padrão {data['label']} CRIADO: {username}")
        else:
            changed = False
            if user.role_id != role.id:
                user.role_id = role.id
                changed = True
            if user.role != data['legacy_role']:
                user.role = data['legacy_role']
                changed = True
                
            if changed:
                logger.warning(f"Tentativa de alteração do usuário {username} revertida.")
                
        # Coletar credenciais para log/demonstração
        generated_credentials.append({
            'perfil': data['label'],
            'login': user.email if user else email,
            'senha': password
        })
        
    db.session.commit()

    # Vincular todos os usuários padrão ao primeiro condomínio real do banco
    try:
        from app.models.condominium import Condominium
        condo = Condominium.query.order_by(Condominium.id).first()
        if condo:
            for username in PROTECTED_USERS.keys():
                user = User.query.filter_by(username=username).first()
                if user and user.condo_id != condo.id:
                    user.condo_id = condo.id
                    logger.info(f"Usuário {username} vinculado ao condomínio: {condo.name}")
            db.session.commit()
        else:
            logger.warning("Nenhum condomínio encontrado no banco. Usuários sem condo_id.")
    except Exception as e:
        logger.error(f"Erro ao vincular usuários ao condomínio: {e}")

    print("\n" + "="*50)
    print("CREDENCIAIS DOS USUÁRIOS PADRÃO (Para demonstração):")
    for cred in generated_credentials:
        print(f"[{cred['perfil']}] Login: {cred['login']} | Senha: {cred['senha']}")
    print("="*50 + "\n")
    
    logger.info("=== VERIFICAÇÃO CONCLUÍDA ===")
