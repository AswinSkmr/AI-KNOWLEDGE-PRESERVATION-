from database import SessionLocal
from models import User

db = SessionLocal()
users = db.query(User).all()

if not users:
    print("No users found in this database at all.")
else:
    for u in users:
        print(u.email, "-", u.role)

db.close()