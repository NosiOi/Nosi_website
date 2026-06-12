from myapp.app import create_app, db

app = create_app()

with app.app_context():
    print("Dropping existing tables...")
    db.drop_all()

    print("Creating all tables...")
    db.create_all()

    print("Database successfully initialized!")
