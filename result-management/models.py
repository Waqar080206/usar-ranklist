# models.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class Branch(str, Enum):
    CSE = "Computer Science Engineering"
    ECE = "Electronics & Communication Engineering"
    EEE = "Electrical & Electronics Engineering"
    MECH = "Mechanical Engineering"
    CIVIL = "Civil Engineering"
    IT = "Information Technology"
    AIDS = "AI & Data Science"
    CSBS = "CS & Business Systems"

class Semester(int, Enum):
    SEM_1 = 1
    SEM_2 = 2
    SEM_3 = 3
    SEM_4 = 4
    SEM_5 = 5
    SEM_6 = 6
    SEM_7 = 7
    SEM_8 = 8

class SubjectResult(BaseModel):
    subject_code: str
    subject_name: str
    internal_marks: float = Field(ge=0, le=40)
    external_marks: float = Field(ge=0, le=60)
    total_marks: float = Field(ge=0, le=100)
    grade: str
    grade_points: float
    credits: int
    status: str  # "PASS" or "FAIL"

class SemesterResult(BaseModel):
    semester: int = Field(ge=1, le=8)
    subjects: List[SubjectResult]
    sgpa: float = Field(ge=0, le=10)
    total_credits: int
    credits_earned: int
    result_status: str  # "PASS", "FAIL", "DETAINED"
    exam_month_year: str
    
class Student(BaseModel):
    roll_number: str = Field(..., regex=r"^[A-Z0-9]+$")
    registration_number: str
    name: str
    father_name: str
    branch: Branch
    batch_year: int = Field(ge=2000, le=2100)
    current_semester: int = Field(ge=1, le=8)
    email: Optional[str] = None
    phone: Optional[str] = None
    semester_results: List[SemesterResult] = []
    cgpa: float = Field(ge=0, le=10, default=0.0)
    overall_status: str = "ACTIVE"  # ACTIVE, GRADUATED, DETAINED, DISCONTINUED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudentSummary(BaseModel):
    """Lightweight model for list views"""
    roll_number: str
    name: str
    branch: str
    current_semester: int
    cgpa: float
    overall_status: str

class BranchStats(BaseModel):
    branch: str
    total_students: int
    pass_count: int
    fail_count: int
    pass_percentage: float
    average_sgpa: float
    toppers: List[StudentSummary]

class SemesterStats(BaseModel):
    semester: int
    branch: str
    total_students: int
    pass_count: int
    fail_count: int
    pass_percentage: float
    average_sgpa: float
    subject_wise_stats: dict