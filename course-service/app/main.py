import os
import httpx
from fastapi import Depends, FastAPI, HTTPException
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
STUDENT_SERVICE_URL = os.getenv("STUDENT_SERVICE_URL", "http://127.0.0.1:8002").rstrip("/")
bearer = HTTPBearer(auto_error=False)
app = FastAPI(title="Course Service", version="1.0.0")
Base.metadata.create_all(bind=engine)
@app.get("/health")
def health(): return {"status":"ok", "service":"course-service"}
def require_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None: raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"): raise ValueError("missing subject")
    except (JWTError, ValueError, TypeError): raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
@app.post("/courses", response_model=schemas.CourseResponse, status_code=201)
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db), _=Depends(require_user)):
    course = models.Course(**payload.model_dump())
    db.add(course)
    try: db.commit(); db.refresh(course)
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409, detail="A course with this name already exists")
    except Exception: db.rollback(); raise HTTPException(status_code=500, detail="Could not create course")
    return course
@app.get("/courses", response_model=list[schemas.CourseResponse])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_user)):
    if skip < 0 or limit < 1 or limit > 500: raise HTTPException(status_code=422, detail="skip must be non-negative and limit must be 1-500")
    return db.query(models.Course).order_by(models.Course.id).offset(skip).limit(limit).all()
@app.get("/courses/{course_id}", response_model=schemas.CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db), _=Depends(require_user)):
    course = db.get(models.Course, course_id)
    if course is None: raise HTTPException(status_code=404, detail="Course not found")
    return course
@app.put("/courses/{course_id}", response_model=schemas.CourseResponse)
def update_course(course_id: int, payload: schemas.CourseUpdate, db: Session = Depends(get_db), _=Depends(require_user)):
    course = db.get(models.Course, course_id)
    if course is None: raise HTTPException(status_code=404, detail="Course not found")
    for key, value in payload.model_dump().items(): setattr(course, key, value)
    try: db.commit(); db.refresh(course)
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409, detail="A course with this name already exists")
    except Exception: db.rollback(); raise HTTPException(status_code=500, detail="Could not update course")
    return course
@app.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db), _=Depends(require_user)):
    course = db.get(models.Course, course_id)
    if course is None: raise HTTPException(status_code=404, detail="Course not found")
    db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).delete(synchronize_session=False)
    db.delete(course); db.commit(); return None
@app.post("/courses/{course_id}/students/{student_id}", response_model=schemas.EnrollmentResponse, status_code=201)
async def enroll_student(course_id: int, student_id: int, credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db), _=Depends(require_user)):
    course = db.get(models.Course, course_id)
    if course is None: raise HTTPException(status_code=404, detail="Course not found")
    if credentials is None: raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{STUDENT_SERVICE_URL}/students/{student_id}", headers={"Authorization": f"Bearer {credentials.credentials}"})
    except httpx.TimeoutException: raise HTTPException(status_code=504, detail="Student service timed out")
    except httpx.RequestError: raise HTTPException(status_code=503, detail="Student service is unavailable")
    if response.status_code == 404: raise HTTPException(status_code=404, detail="Student not found")
    if response.status_code == 401: raise HTTPException(status_code=401, detail="Student service rejected token")
    if response.status_code >= 400: raise HTTPException(status_code=503, detail="Could not verify student")
    enrollment = models.Enrollment(course_id=course_id, student_id=student_id)
    db.add(enrollment)
    try: db.commit(); db.refresh(enrollment)
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409, detail="Student is already enrolled in this course")
    return enrollment
@app.get("/courses/{course_id}/students", response_model=list[schemas.EnrolledStudent])
async def course_students(course_id: int, credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db), _=Depends(require_user)):
    course = db.get(models.Course, course_id)
    if course is None: raise HTTPException(status_code=404, detail="Course not found")
    if credentials is None: raise HTTPException(status_code=401, detail="Bearer token required")
    ids = [row.student_id for row in db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).all()]
    students = []
    for student_id in ids:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{STUDENT_SERVICE_URL}/students/{student_id}", headers={"Authorization": f"Bearer {credentials.credentials}"})
        except httpx.TimeoutException: raise HTTPException(status_code=504, detail="Student service timed out")
        except httpx.RequestError: raise HTTPException(status_code=503, detail="Student service is unavailable")
        if response.status_code == 200: students.append(response.json())
    return students
