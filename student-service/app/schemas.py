from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
class StudentBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    department: str = Field(min_length=2, max_length=120)
    course: str = Field(min_length=2, max_length=120)
    @field_validator("name", "department", "course")
    @classmethod
    def non_blank(cls, value):
        if not value.strip(): raise ValueError("This field cannot be blank")
        return value.strip()
class StudentCreate(StudentBase): pass
class StudentUpdate(StudentBase): pass
class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
