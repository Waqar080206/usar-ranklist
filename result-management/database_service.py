"""
USAR Ranklist - Data Service
Handles data loading and ranking logic
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional


# Branch codes mapping
BRANCHES = {
    "519": {"code": "AIDS", "name": "Artificial Intelligence & Data Science"},
    "516": {"code": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    "520": {"code": "IIOT", "name": "Industrial Internet of Things"},
    "517": {"code": "AR", "name": "Automation & Robotics"},
}

# Default filter options (always available)
DEFAULT_BRANCHES = [
    {"code": "519", "short": "AIDS", "name": "Artificial Intelligence & Data Science"},
    {"code": "516", "short": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    {"code": "520", "short": "IIOT", "name": "Industrial Internet of Things"},
    {"code": "517", "short": "AR", "name": "Automation & Robotics"},
]

DEFAULT_SEMESTERS = ["01", "02", "03", "04", "05", "06", "07", "08"]
DEFAULT_BATCHES = ["2024", "2023", "2022", "2021"]

# Grade to points mapping
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}


class DataService:
    def __init__(self):
        self.students: List[Dict] = []
        self._loaded = False
        self._load_error = None
    
    def _find_data_file(self) -> Optional[Path]:
        """Find the data file in various possible locations"""
        current_dir = Path(__file__).resolve().parent
        
        possible_paths = [
            current_dir / "data" / "parsed_results.json",
            current_dir / "parsed_results.json",
            current_dir.parent / "data" / "output" / "parsed_results.json",
            current_dir.parent / "data" / "parsed_results.json",
            Path("/var/task/result-management/data/parsed_results.json"),
            Path("/var/task/data/parsed_results.json"),
        ]
        
        for path in possible_paths:
            if path and path.exists():
                return path
        
        return None
    
    def load_data(self) -> bool:
        """Load data from JSON file"""
        if self._loaded:
            return len(self.students) > 0
        
        file_path = self._find_data_file()
        
        if not file_path:
            self._load_error = "Data file not found"
            self._loaded = True
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            self.students = []
            for record in raw_data:
                student = self._process_student(record)
                if student:
                    self.students.append(student)
            
            self._loaded = True
            return True
            
        except Exception as e:
            self._load_error = str(e)
            self._loaded = True
            return False
    
    def _process_student(self, record: Dict) -> Optional[Dict]:
        """Process and enrich student record"""
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
        """Calculate SGPA from subjects"""
        total_credits = 0
        weighted_sum = 0.0
        
        for sub in subjects:
            credits = sub.get('credits', 0) or 0
            grade = sub.get('grade', 'F') or 'F'
            
            if credits > 0:
                grade_point = GRADE_POINTS.get(grade, 0)
                weighted_sum += credits * grade_point
                total_credits += credits
        
        if total_credits > 0:
            return round(weighted_sum / total_credits, 2)
        
        return round(percentage / 10, 2) if percentage else 0.0
    
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
        
        ranklist = []
        for idx, student in enumerate(filtered):
            ranklist.append({
                "rank": idx + 1,
                "roll_no": student["roll_no"],
                "name": student["name"],
                "branch": student["branch"],
                "semester": student["semester"],
                "batch": student["batch"],
                "percentage": student["percentage"],
                "sgpa": student["sgpa"],
                "credits": student["credits"]
            })
        
        return {
            "total": len(ranklist),
            "filters": {
                "branch": branch,
                "semester": semester,
                "batch": batch,
                "sort_by": sort_by,
                "order": "ascending" if ascending else "descending"
            },
            "ranklist": ranklist
        }
    
    def get_filter_options(self) -> Dict:
        """Get available filter options - ALWAYS returns options"""
        if not self._loaded:
            self.load_data()
        
        # Always return default branches
        branches = DEFAULT_BRANCHES.copy()
        
        # Try to get semesters and batches from data, fallback to defaults
        if self.students:
            semesters = sorted(set(s["semester"] for s in self.students if s.get("semester")))
            batches = sorted(set(s["batch"] for s in self.students if s.get("batch")), reverse=True)
            
            # Use defaults if empty
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
            "error": self._load_error
        }
    
    def get_student_by_roll(self, roll_no: str) -> Optional[Dict]:
        """Get student by roll number"""
        if not self._loaded:
            self.load_data()
        
        for student in self.students:
            if student["roll_no"] == roll_no:
                return student
        return None
    
    def get_stats(
        self,
        branch: Optional[str] = None,
        semester: Optional[str] = None,
        batch: Optional[str] = None
    ) -> Dict:
        """Get statistics for filtered students"""
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
            "highest_sgpa": max(sgpas) if sgpas else 0,
            "highest_percentage": max(percentages) if percentages else 0,
            "topper": ranklist[0] if ranklist else None
        }


# Singleton
data_service = DataService()