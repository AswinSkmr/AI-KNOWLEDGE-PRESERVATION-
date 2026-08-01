from database import SessionLocal
from models import User, Document

db = SessionLocal()
admin = db.query(User).filter(User.email == "admin@test.com").first()

doc = Document(
    title="Sample Data Structures Textbook",
    description="Introductory textbook covering arrays, trees, and graphs.",
    document_type="textbook",
    category="Computer Science",
    file_name="placeholder.pdf",
    original_file_name="Data_Structures.pdf",
    file_path="/uploads/placeholder.pdf",
    file_size=1048576,
    mime_type="application/pdf",
    uploaded_by=admin.id,
)
db.add(doc)
db.commit()

print("Created document:", doc.document_id)
print("Uploaded by:", doc.uploader.full_name)
db.close()