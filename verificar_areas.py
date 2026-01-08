from app import create_app, db
from app.models.amenity import CommonArea

app = create_app()

with app.app_context():
    areas = CommonArea.query.all()
    print(f"Total de areas encontradas: {len(areas)}")
    
    if len(areas) == 0:
        print("Criando areas padrao para teste...")
        a1 = CommonArea(name='Churrasqueira', description='Churrasqueira completa com freezer e mesas.', capacity=20)
        a2 = CommonArea(name='Salão de Festas', description='Salao climatizado com cozinha de apoio.', capacity=80)
        a3 = CommonArea(name='Quadra de Esportes', description='Quadra poliesportiva (Futebol/Volei).', capacity=30)
        
        db.session.add(a1)
        db.session.add(a2)
        db.session.add(a3)
        db.session.commit()
        print("Areas criadas! Atualize a pagina.")
    else:
        for a in areas:
            print(f"- {a.name}")
