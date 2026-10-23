from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
class CourseBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1000)
    department: str = Field(min_length=2, max_length=120)
    @field_validator("name", "department")
    @classmethod
    def non_blank(cls, value):
        if not value.strip(): raise ValueError("This field cannot be blank")
        return value.strip()
class CourseCreate(CourseBase): pass
class CourseUpdate(CourseBase): pass
class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
class EnrollmentResponse(BaseModel):
    id: int
    course_id: int
    student_id: int
    enrolled_at: datetime
class EnrolledStudent(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    department: str
    course: str
