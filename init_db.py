from app import app, db

# Pastikan berada dalam konteks aplikasi Flask
with app.app_context():
    db.create_all()
    print("Database created!")
