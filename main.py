from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

class UserSignup(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str


@app.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # Base case: Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User Already Exists")

    new_user = User (name=user.name, username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message":"User created successfully", "user":{"id":new_user.id, "email": new_user.email}}


@app.delete("/users/{user_email}")
def delete(user_email: str, db: Session = Depends(get_db)):
        existing_user = db.query(User).filter(User.email == user_email).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User Does Not Exists")
        db.delete(existing_user)
        db.commit()

        return {"message":"User deleted successfully", "email":user_email}

@app.get("/users/info/{user_name}")
def info(user_name: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_name).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User Does Not Exist")

    return {"message":"First name and email of:", "name":existing_user.name, "email":existing_user.email}
