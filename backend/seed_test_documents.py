from database import SessionLocal
from models import Document, User

db = SessionLocal()
admin = db.query(User).filter(User.email == "admin@test.com").first()

sample_docs = [
    ("Data Structures and Algorithms", "textbook", "Computer Science", 2_500_000),
    ("Operating Systems Concepts", "textbook", "Computer Science", 4_100_000),
    ("Database Management Systems", "textbook", "Computer Science", 3_200_000),
    ("Digital Signal Processing", "textbook", "Electronics", 5_000_000),
    ("Automated Attendance System", "project_report", "Computer Science", 1_200_000),
    ("Smart Irrigation Using IoT", "project_report", "Electronics", 900_000),
    ("AI Chatbot for Customer Support", "project_report", "Computer Science", 1_800_000),
    ("Linear Algebra Fundamentals", "textbook", "Mathematics", 2_000_000),
    ("Blockchain Voting System", "project_report", "Computer Science", 1_500_000),
    ("Computer Networks Essentials", "textbook", "Computer Science", 3_700_000),
    ("Solar Powered Vehicle Design", "project_report", "Mechanical", 2_200_000),
    ("Discrete Mathematics", "textbook", "Mathematics", 1_900_000),
    ("Face Recognition Attendance", "project_report", "Computer Science", 1_100_000),
]

for title, doc_type, category, size in sample_docs:
    doc = Document(
        title=title,
        description=f"Sample entry for testing — {title}",
        document_type=doc_type,
        category=category,
        file_name=f"placeholder-{title[:10].replace(' ', '_')}.pdf",
        original_file_name=f"{title}.pdf",
        file_path="/uploads/placeholder.pdf",
        file_size=size,
        mime_type="application/pdf",
        uploaded_by=admin.id,
    )
    db.add(doc)

db.commit()
print(f"Created {len(sample_docs)} test documents")
db.close()