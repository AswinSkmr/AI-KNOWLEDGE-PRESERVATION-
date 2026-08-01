import requests

BASE_URL = "http://127.0.0.1:8000"

# Step 1: log in and get a token
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@test.com", "password": "testpassword123"},
)
print("Login status:", login_response.status_code)
print("Login response:", login_response.json())

token = login_response.json()["access_token"]

# Step 2: upload a real PDF using that token
# CHANGE THIS to a real path to a PDF that actually exists on your machine
pdf_path = r"C:\Users\measw\Downloads\ASWIN S CV_compressed.pdf"
with open(pdf_path, "rb") as f:
    upload_response = requests.post(
        f"{BASE_URL}/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"title": "Test Upload", "document_type": "textbook"},
        files={"file": (pdf_path.split("\\")[-1], f, "application/pdf")},
    )

print("Upload status:", upload_response.status_code)
print("Upload response:", upload_response.json())