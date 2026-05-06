import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app
app = create_app()

with app.test_client() as client:
    response = client.get('/auth/login', follow_redirects=True)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("ERROR IN RENDER TEMPLATE OR ROUTE")
        print(response.data.decode('utf-8'))
    else:
        print("GET /auth/login SUCCEEDED")
