from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User
import bcrypt

# Password hashing
# Configure passlib to use bcrypt with proper settings
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__ident="2b")

# JWT settings (for session tokens)
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Ensure password is a string
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode('utf-8')
    elif not isinstance(plain_password, str):
        plain_password = str(plain_password)
    
    # Strip whitespace
    plain_password = plain_password.strip()
    
    # Convert to bytes for bcrypt
    password_bytes = plain_password.encode('utf-8')
    
    # Bcrypt has a 72-byte limit
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Convert hashed_password to bytes if it's a string
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode('utf-8')
    else:
        hashed_bytes = hashed_password
    
    # Use bcrypt directly to verify
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # Fallback to passlib if bcrypt fails
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Ensure password is a string
    if isinstance(password, bytes):
        password = password.decode('utf-8', errors='replace')
    elif not isinstance(password, str):
        password = str(password)
    
    # Strip whitespace
    password = password.strip()
    
    # Convert to bytes for bcrypt (bcrypt works with bytes)
    password_bytes = password.encode('utf-8')
    
    # Bcrypt has a 72-byte limit - truncate if necessary
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Use bcrypt directly to hash the password
    # This avoids any passlib configuration issues
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string (passlib format expects string)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user_from_token(token: str, db: Session):
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            print(f"Token payload missing 'sub': {payload}")
            raise credentials_exception
        
        # Ensure user_id is an integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            print(f"Invalid user_id type in token: {user_id} (type: {type(user_id)})")
            raise credentials_exception
            
    except JWTError as e:
        print(f"JWT decode error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"User not found with id: {user_id}")
        raise credentials_exception
    return user

