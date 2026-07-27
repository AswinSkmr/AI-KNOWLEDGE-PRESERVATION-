from database import SessionLocal
from models import User
from security import hash_password

db = SessionLocal()
user = User(
    full_name="Test Admin",
    email="admin@test.com",
    password_hash=hash_password("testpassword123"),
    role="admin",
)
db.add(user)
db.commit()
print("Created user:", user.id)
db.close()