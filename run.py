from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting server accessible on network...")
    app.run(host='0.0.0.0', debug=True)
