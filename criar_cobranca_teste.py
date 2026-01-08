from app import create_app, db
from app.models.user import User
from app.models.core import Payment
from datetime import date, timedelta

app = create_app()

def create_test_payment():
    with app.app_context():
        print("--- Gerador de Cobrança de Teste ---")
        
        # 1. Find a target user (prefer resident, but fallback to admin if needed for testing)
        residents = User.query.filter_by(role='resident').all()
        
        if not residents:
            print("Nenhum morador encontrado. Tentando adicionar para o admin (apenas para teste de visualização)...")
            target_user = User.query.filter_by(username='admin').first()
        else:
            print(f"Encontrados {len(residents)} moradores.")
            target_user = residents[0] # Pick the first one
            
        if not target_user:
            print("ERRO: Nenhum usuário encontrado no sistema.")
            return

        print(f"Gerando cobrança para: {target_user.username} (ID: {target_user.id})")
        
        # 2. Create the payment
        amount = 150.00
        due_date = date.today() + timedelta(days=5) # Due in 5 days
        
        payment = Payment(
            user_id=target_user.id,
            description="Taxa Condominial - Teste Visual",
            amount=amount,
            status='pending',
            due_date=due_date
        )
        
        db.session.add(payment)
        db.session.commit()
        
        print("Sucesso! Cobrança criada.")
        print(f"Valor: R$ {amount}")
        print(f"Vencimento: {due_date.strftime('%d/%m/%Y')}")
        print("\nAGORA: Faça login como esse usuário (ou vá no painel se for o seu) para ver os botões de pagamento.")

if __name__ == "__main__":
    create_test_payment()
