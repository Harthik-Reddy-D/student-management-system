import os
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from . import models, schemas
from .database import Base, engine, get_db
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET", "replace-with-a-long-random-secret-before-use")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
bearer = HTTPBearer(auto_error=False)
app = FastAPI(title="Student Service", version="1.0.0")
Base.metadata.create_all(bind=engine)
@app.get("/health")
def health(): return {"status":"ok", "service":"student-service"}
def require_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None: raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"): raise ValueError("missing subject")
    except (JWTError, ValueError, TypeError): raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
@app.post("/students", response_model=schemas.StudentResponse, status_code=201)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db), _=Depends(require_user)):
    student = models.Student(**payload.model_dump(exclude={"email"}), email=str(payload.email).lower())
    db.add(student)
    try: db.commit(); db.refresh(student)
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409, detail="A student with this email already exists")
    except Exception: db.rollback(); raise HTTPException(status_code=500, detail="Could not create student")
    return student
@app.get("/students", response_model=list[schemas.StudentResponse])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_user)):
    if skip < 0 or limit < 1 or limit > 500: raise HTTPException(status_code=422, detail="skip must be non-negative and limit must be 1-500")
    return db.query(models.Student).order_by(models.Student.id).offset(skip).limit(limit).all()
@app.get("/students/{student_id}", response_model=schemas.StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db), _=Depends(require_user)):
    student = db.get(models.Student, student_id)
    if student is None: raise HTTPException(status_code=404, detail="Student not found")
    return student
@app.put("/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db), _=Depends(require_user)):
    student = db.get(models.Student, student_id)
    if student is None: raise HTTPException(status_code=404, detail="Student not found")
    for key, value in payload.model_dump().items(): setattr(student, key, str(value).lower() if key == "email" else value)
    try: db.commit(); db.refresh(student)
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409, detail="A student with this email already exists")
    except Exception: db.rollback(); raise HTTPException(status_code=500, detail="Could not update student")
    return student
@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db), _=Depends(require_user)):
    student = db.get(models.Student, student_id)
    if student is None: raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student); db.commit(); return None
