"""
USAR Ranklist - Data Models
Pydantic models for student results management
"""

from pydantic import BaseModel
from typing import Optional, List, Dict


# ============ Constants ============

# Grade points mapping (IPU grading system)
GRADE_POINTS = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "P": 4,
    "F": 0,
}


# ============ Branch Information ============

class BranchInfo:
    """Branch information for USAR - 4 branches"""
    BRANCHES = {
        "519": {"code": "AIDS", "name": "Artificial Intelligence & Data Science"},
        "516": {"code": "AIML", "name": "Artificial Intelligence & Machine Learning"},
        "520": {"code": "IIOT", "name": "Industrial Internet of Things"},
        "517": {"code": "AR", "name": "Automation & Robotics"},
    }
    
    @classmethod
    def get_branch(cls, code: str) -> Dict:
        return cls.BRANCHES.get(code, {"code": "Unknown", "name": "Unknown Branch"})
    
    @classmethod
    def get_all_branches(cls) -> List[Dict]:
        return [
            {"branch_code": k, **v} 
            for k, v in cls.BRANCHES.items()
        ]


# ============ Subject Model (MUST be before Student) ============

class Subject(BaseModel):
    """Individual subject result"""
    paper_id: str = ""
    paper_name: str = ""
    credits: int = 0
    internal: Optional[int] = None
    external: Optional[int] = None
    total: Optional[int] = None
    grade: str = "F"
    grade_point: float = 0.0
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculate grade point from grade
        self.grade_point = float(GRADE_POINTS.get(self.grade, 0))


# ============ Enrollment Details ============

class EnrollmentDetails(BaseModel):
    """Parsed enrollment number details"""
    roll_no: str
    class_roll: str = ""
    school_code: str = ""
    branch_code: str = ""
    admission_year: str = ""
    branch_short: str = ""
    branch_name: str = ""
    
    @classmethod
    def parse(cls, roll_no: str) -> "EnrollmentDetails":
        """
        Parse enrollment number
        Format: XXXYYYZZZAA (11 digits)
        Example: 05919051924
        - 059 = Class Roll
        - 190 = School Code (USAR)
        - 519 = Branch Code (AIDS)
        - 24 = Admission Year (2024)
        """
        roll = str(roll_no).strip()
        
        if len(roll) >= 11:
            class_roll = roll[0:3]
            school_code = roll[3:6]
            branch_code = roll[6:9]
            admission_year = roll[9:11]
        elif len(roll) >= 9:
            class_roll = roll[0:3]
            school_code = roll[3:6]
            branch_code = roll[6:9]
            admission_year = ""
        else:
            return cls(roll_no=roll_no)
        
        branch_info = BranchInfo.get_branch(branch_code)
        
        return cls(
            roll_no=roll_no,
            class_roll=class_roll,
            school_code=school_code,
            branch_code=branch_code,
            admission_year=admission_year,
            branch_short=branch_info["code"],
            branch_name=branch_info["name"]
        )


# ============ Student Model ============

class Student(BaseModel):
    """Complete student record"""
    rank: Optional[int] = None
    roll_no: str = ""
    name: str = ""
    sid: str = ""
    institution: str = "UNIVERSITY SCHOOL OF AUTOMATION AND ROBOTICS"
    programme: str = ""
    semester: str = ""
    batch: str = ""
    total_marks: int = 0
    max_marks: int = 0
    percentage: float = 0.0
    credits_secured: int = 0
    subjects: List[Subject] = []
    
    # Calculated/Derived fields
    sgpa: float = 0.0
    branch_code: str = ""
    branch_short: str = ""
    branch_name: str = ""
    admission_year: str = ""
    
    class Config:
        # Allow mutation for calculating fields
        validate_assignment = True
    
    def calculate_sgpa(self) -> float:
        """Calculate SGPA from subjects"""
        total_credits = 0
        weighted_sum = 0.0
        
        for subject in self.subjects:
            if subject.credits and subject.credits > 0:
                grade_point = GRADE_POINTS.get(subject.grade, 0)
                weighted_sum += subject.credits * grade_point
                total_credits += subject.credits
        
        if total_credits > 0:
            self.sgpa = round(weighted_sum / total_credits, 2)
        else:
            # Fallback: estimate from percentage
            self.sgpa = round(self.percentage / 10, 2) if self.percentage else 0.0
        
        return self.sgpa
    
    def parse_enrollment(self):
        """Parse enrollment number and set branch info"""
        details = EnrollmentDetails.parse(self.roll_no)
        self.branch_code = details.branch_code
        self.branch_short = details.branch_short
        self.branch_name = details.branch_name
        self.admission_year = f"20{details.admission_year}" if details.admission_year else ""


# ============ Summary Models ============

class StudentSummary(BaseModel):
    """Lightweight student summary for list views"""
    rank: int = 0
    roll_no: str = ""
    name: str = ""
    branch: str = ""
    semester: str = ""
    batch: str = ""
    percentage: float = 0.0
    sgpa: float = 0.0
    credits_secured: int = 0


class BranchStats(BaseModel):
    """Statistics for a branch"""
    branch_code: str = ""
    branch_short: str = ""
    branch_name: str = ""
    total_students: int = 0
    average_percentage: float = 0.0
    average_sgpa: float = 0.0
    highest_percentage: float = 0.0
    highest_sgpa: float = 0.0
    lowest_sgpa: float = 0.0
    pass_count: int = 0
    fail_count: int = 0
    pass_percentage: float = 0.0
    toppers: List[StudentSummary] = []


class SemesterStats(BaseModel):
    """Statistics for a semester"""
    semester: str = ""
    total_students: int = 0
    average_percentage: float = 0.0
    average_sgpa: float = 0.0
    pass_count: int = 0
    fail_count: int = 0
    branches: Dict[str, int] = {}


class FilterOptions(BaseModel):
    """Available filter options for UI"""
    branches: List[Dict] = []
    semesters: List[str] = []
    batches: List[str] = []