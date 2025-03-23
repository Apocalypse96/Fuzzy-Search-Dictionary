import bcrypt
import sys

def generate_hash(password):
    """Generate a bcrypt hash for the given password."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_hash(password, hashed):
    """Verify a password against a hash."""
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

if __name__ == "__main__":
    # Generate a new hash for the password
    password = "password"  # Default password
    if len(sys.argv) > 1:
        password = sys.argv[1]
    
    new_hash = generate_hash(password)
    print(f"Generated hash: {new_hash}")
    
    # Verify the hash works
    is_valid = verify_hash(password, new_hash)
    print(f"Verification successful: {is_valid}")
