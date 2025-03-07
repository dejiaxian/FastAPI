# Repository layer to handle database queries
from sqlalchemy.orm import Session
from database import User
from schemas import UserCreate, UserUpdate

# Create a new user
def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, name=user.name, position=user.position, university=user.university)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all users
def get_users(db: Session):
    return db.query(User).all()

# Get a single user by email
def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Update user details
def update_user(db: Session, email: str, user_data: UserUpdate):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# Delete user
def delete_user(db: Session, email: str):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
