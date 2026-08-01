from database import SessionLocal
from models import User
from security import hash_password

db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@test.com").first()
if existing:
    print("Admin already exists:", existing.email)
else:
    admin = User(
        university_id="ADMIN-0001",
        full_name="Test Admin",
        email="admin@test.com",
        password_hash=hash_password("testpassword123"),
        role="admin",
    )
    db.add(admin)
    db.commit()
    print("Created admin:", admin.email)

db.close()