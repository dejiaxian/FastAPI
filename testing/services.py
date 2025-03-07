# Business logic (data model layer)
from sqlalchemy.orm import Session
from schemas import UserCreate, UserUpdate
from crud import create_user, get_user, update_user, delete_user, get_users
from fastapi import HTTPException

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate):
        # Ensure unique email
        if get_user(self.db, user.email):
            raise HTTPException(status_code=400, detail="Email already exists")

        # Custom validation (e.g., only alphabetic characters for name, position, university)
        if not user.name.replace(" ", "").isalpha() or not user.position.replace(" ", "").isalpha() or not user.university.replace(" ", "").isalpha():
            raise HTTPException(status_code=400, detail="Only alphabets and spaces are allowed in name, position, and university")
        
        if len(user.name) < 2 or len(user.name) > 50:
            raise HTTPException(status_code=400, detail="Name must be between 2 and 50 characters")

        return create_user(self.db, user)

    def get_users(self):
        return get_users(self.db)

    def get_user(self, email: str):
        user = get_user(self.db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user(self, email: str, user_data: UserUpdate):
        user = update_user(self.db, email, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def delete_user(self, email: str):
        user = delete_user(self.db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
