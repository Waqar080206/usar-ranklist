"""
USAR Ranklist - Data Service
Handles data loading and ranking logic
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

# Try to import embedded data (for Vercel)
try:
    from embedded_data import STUDENT_DATA
    HAS_EMBEDDED_DATA = True
except ImportError:
    STUDENT_DATA = []
    HAS_EMBEDDED_DATA = False


# Branch codes mapping
BRANCHES = {
    "519": {"code": "AIDS", "name": "Artificial Intelligence & Data Science"},
    "516": {"code": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    "520": {"code": "IIOT", "name": "Industrial Internet of Things"},
    "517": {"code": "AR", "name": "Automation & Robotics"},
}

# Default filter options
DEFAULT_BRANCHES = [
    {"code": "519", "short": "AIDS", "name": "Artificial Intelligence & Data Science"},
    {"code": "516", "short": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    {"code": "520", "short": "IIOT", "name": "Industrial Internet of Things"},
    {"code": "517", "short": "AR", "name": "Automation & Robotics"},
]

DEFAULT_SEMESTERS = ["01", "02", "03", "04", "05", "06", "07", "08"]
DEFAULT_BATCHES = ["2024", "2023", "2022", "2021"]

GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}


class DataService:
    def __init__(self):
        self.students: List[Dict] = []
        self._loaded = False
        self._load_error = None
    
    def _find_data_file(self) -> Optional[Path]:
        """Find JSON data file"""
        current_dir = Path(__file__).resolve().parent
        
        paths = [
            current_dir / "data" / "parsed_results.json",
            current_dir / "parsed_results.json",
            current_dir.parent / "data" / "output" / "parsed_results.json",
        ]
        
        for path in paths:
            if path.exists():
                return path
        return None
    
    def load_data(self) -> bool:
        """Load data from embedded data or JSON file"""
        if self._loaded:
            return len(self.students) > 0
        
        raw_data = []
        
        # Try embedded data first (for Vercel)
        if HAS_EMBEDDED_DATA and STUDENT_DATA:
            raw_data = STUDENT_DATA
            print(f"✅ Using embedded data: {len(raw_data)} records")
        else:
            # Try loading from file
            file_path = self._find_data_file()
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    print(f"✅ Loaded from file: {len(raw_data)} records")
                except Exception as e:
                    self._load_error = str(e)
            else:
                self._load_error = "No data source found"
        
        # Process records
        self.students = []
        for record in raw_data:
            student = self._process_student(record)
            if student:
                self.students.append(student)
        
        self._loaded = True
        print(f"✅ Processed {len(self.students)} students")
        return len(self.students) > 0
    
    def _process_student(self, record: Dict) -> Optional[Dict]:
        """Process student record"""
        try:
            roll_no = str(record.get('roll_no', ''))
            branch_code = roll_no[6:9] if len(roll_no) >= 9 else ""
            branch_info = BRANCHES.get(branch_code, {"code": "Unknown", "name": "Unknown"})
            
            subjects = record.get('subjects', [])
            sgpa = self._calculate_sgpa(subjects, record.get('percentage', 0))
            
            return {
                "roll_no": roll_no,
                "name": record.get('name', ''),
                "branch_code": branch_code,
                "branch": branch_info["code"],
                "branch_name": branch_info["name"],
                "semester": str(record.get('semester', '')),
                "batch": str(record.get('batch', '')),
                "total_marks": record.get('total_marks', 0) or 0,
                "max_marks": record.get('max_marks', 0) or 0,
                "percentage": float(record.get('percentage', 0) or 0),
                "sgpa": sgpa,
                "credits": record.get('credits_secured', 0) or 0,
                "subjects": subjects
            }
        except Exception:
            return None
    
    def _calculate_sgpa(self, subjects: List, percentage: float) -> float:
        """Calculate SGPA"""
        total_credits = 0
        weighted_sum = 0.0
        
        for sub in subjects:
            credits = sub.get('credits', 0) or 0
            grade = sub.get('grade', 'F') or 'F'
            if credits > 0:
                weighted_sum += credits * GRADE_POINTS.get(grade, 0)
                total_credits += credits
        
        if total_credits > 0:
            return round(weighted_sum / total_credits, 2)
        return round(percentage / 10, 2) if percentage else 0.0
    
    def get_filter_options(self) -> Dict:
        """Get filter options - always returns options"""
        if not self._loaded:
            self.load_data()
        
        branches = DEFAULT_BRANCHES.copy()
        
        if self.students:
            semesters = sorted(set(s["semester"] for s in self.students if s.get("semester")))
            batches = sorted(set(s["batch"] for s in self.students if s.get("batch")), reverse=True)
            if not semesters:
                semesters = DEFAULT_SEMESTERS
            if not batches:
                batches = DEFAULT_BATCHES
        else:
            semesters = DEFAULT_SEMESTERS
            batches = DEFAULT_BATCHES
        
        return {
            "branches": branches,
            "semesters": semesters,
            "batches": batches,
            "total_students": len(self.students),
            "data_loaded": len(self.students) > 0,
            "has_embedded": HAS_EMBEDDED_DATA,
            "error": self._load_error
        }
    
    def get_ranklist(
        self,
        branch: Optional[str] = None,
        semester: Optional[str] = None,
        batch: Optional[str] = None,
        sort_by: str = "sgpa",
        ascending: bool = False
    ) -> Dict:
        """Get ranklist with filters"""
        if not self._loaded:
            self.load_data()
        
        filtered = self.students.copy()
        
        if branch:
            branch_upper = branch.upper()
            filtered = [s for s in filtered 
                       if s["branch"].upper() == branch_upper or s["branch_code"] == branch]
        
        if semester:
            filtered = [s for s in filtered if s["semester"] == semester]
        
        if batch:
            filtered = [s for s in filtered if s["batch"] == batch]
        
        if sort_by == "sgpa":
            filtered.sort(key=lambda x: x["sgpa"], reverse=not ascending)
        else:
            filtered.sort(key=lambda x: x["percentage"], reverse=not ascending)
        
        ranklist = [{
            "rank": idx + 1,
            "roll_no": s["roll_no"],
            "name": s["name"],
            "branch": s["branch"],
            "semester": s["semester"],
            "batch": s["batch"],
            "percentage": s["percentage"],
            "sgpa": s["sgpa"],
            "credits": s["credits"]
        } for idx, s in enumerate(filtered)]
        
        return {
            "total": len(ranklist),
            "filters": {"branch": branch, "semester": semester, "batch": batch},
            "ranklist": ranklist
        }
    
    def get_student_by_roll(self, roll_no: str) -> Optional[Dict]:
        """Get student by roll number"""
        if not self._loaded:
            self.load_data()
        
        for student in self.students:
            if student["roll_no"] == roll_no:
                return student
        return None
    
    def get_stats(self, branch=None, semester=None, batch=None) -> Dict:
        """Get statistics"""
        result = self.get_ranklist(branch, semester, batch)
        ranklist = result["ranklist"]
        
        if not ranklist:
            return {"total": 0, "avg_sgpa": 0, "avg_percentage": 0, "topper": None}
        
        sgpas = [s["sgpa"] for s in ranklist if s["sgpa"] > 0]
        percentages = [s["percentage"] for s in ranklist if s["percentage"] > 0]
        
        return {
            "total": len(ranklist),
            "avg_sgpa": round(sum(sgpas) / len(sgpas), 2) if sgpas else 0,
            "avg_percentage": round(sum(percentages) / len(percentages), 2) if percentages else 0,
            "topper": ranklist[0] if ranklist else None
        }


data_service = DataService()