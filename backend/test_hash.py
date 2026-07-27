from security import hash_password, verify_password

test_hash = hash_password("testpassword123")
print("Generated hash:", test_hash)
print("Verify correct password:", verify_password("testpassword123", test_hash))
print("Verify wrong password:", verify_password("wrongpassword", test_hash))