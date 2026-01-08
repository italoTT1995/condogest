from app import create_app

app = create_app()
print(f"I am connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
