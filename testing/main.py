from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, User, Base
from pydantic import BaseModel, EmailStr, field_validator
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Allow requests from any origin 
    allow_credentials=True, # Allow credentials (e.g. Cookies, Auth Tokens)
    allow_methods=["*"],    # Allow all HTTP methods (e.g. GET, POST, PUT, DELETE)
    allow_headers=["*"],    # Allow all HTTP headers (e.g. Authorization, Content-Type)
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Welcome message
@app.get("/")
def welcome_message():
    return {"message": "Welcome to my FastAPI app!"}

# Pydantic model for user input validation
class UserCreate(BaseModel):
    name: str
    email: EmailStr  
    position: str  
    university: str  

    # Validation for name, university, and position to only consist of alphabetical characters
    @field_validator("name", "position", "university")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        if not value.replace(" ", "").isalpha():
            raise HTTPException(status_code=400, detail="Only alphabets and spaces are allowed")

        if len(value) < 2 or len(value) > 50:
            raise HTTPException(status_code=400, detail="Value must be between 2 and 50 characters")
        return value

# Add a new user
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    # Prevent duplicate user registrations 
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(email=user.email, name=user.name, position=user.position, university=user.university)

    # Save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User added successfully!"}

# Get all users
@app.get("/all-users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"name": user.name, "email": user.email, "position": user.position, 
            "university": user.university} for user in users]

# Get a single user by email
@app.get("/users/{email}")
def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update a user's name, position, or university based on their email
@app.put("/users/{email}")
def update_user(email: str, name: str = None, position: str = None, university: str = None, 
                db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only if new values are provided
    if name:
        user.name = name
    if position:
        user.position = position
    if university:
        user.university = university

    db.commit()
    db.refresh(user)  # Refresh the object to reflect updated values
    return {"message": "User updated successfully!", "user": user}

# Delete a user
@app.delete("/users/{email}")
def delete_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully!"}
