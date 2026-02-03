"""
USAR Ranklist - Data Service
Handles data loading and ranking logic
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


# Branch codes mapping
BRANCHES = {
    "519": {"code": "AIDS", "name": "Artificial Intelligence & Data Science"},
    "516": {"code": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    "520": {"code": "IIOT", "name": "Industrial Internet of Things"},
    "517": {"code": "AR", "name": "Automation & Robotics"},
}

# Grade to points mapping
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}


class DataService:
    def __init__(self):
        self.students: List[Dict] = []
        self._loaded = False
    
    def load_data(self) -> bool:
        """Load data from JSON file"""
        if self._loaded:
            return True
        
        # Find data file
        possible_paths = [
            Path(__file__).parent.parent / "data" / "output" / "parsed_results.json",
            Path("w:/usar-ranklist/data/output/parsed_results.json"),
            Path("../data/output/parsed_results.json"),
        ]
        
        file_path = None
        for path in possible_paths:
            if path.exists():
                file_path = path
                break
        
        if not file_path:
            print("❌ Data file not found!")
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
            print(f"✅ Loaded {len(self.students)} students from {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _process_student(self, record: Dict) -> Optional[Dict]:
        """Process and enrich student record"""
        try:
            roll_no = str(record.get('roll_no', ''))
            
            # Parse branch from roll number (digits 7-9)
            branch_code = roll_no[6:9] if len(roll_no) >= 9 else ""
            branch_info = BRANCHES.get(branch_code, {"code": "Unknown", "name": "Unknown"})
            
            # Calculate SGPA from subjects
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
        except Exception as e:
            print(f"⚠️ Error processing: {e}")
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
        
        # Fallback: estimate from percentage
        return round(percentage / 10, 2) if percentage else 0.0
    
    def get_ranklist(
        self,
        branch: Optional[str] = None,
        semester: Optional[str] = None,
        batch: Optional[str] = None,
        sort_by: str = "sgpa",
        ascending: bool = False
    ) -> Dict:
        """
        Get ranklist with filters
        Returns ranked list sorted by SGPA or Percentage
        """
        if not self._loaded:
            self.load_data()
        
        # Filter students
        filtered = self.students.copy()
        
        if branch:
            branch_upper = branch.upper()
            filtered = [s for s in filtered 
                       if s["branch"].upper() == branch_upper or s["branch_code"] == branch]
        
        if semester:
            filtered = [s for s in filtered if s["semester"] == semester]
        
        if batch:
            filtered = [s for s in filtered if s["batch"] == batch]
        
        # Sort by SGPA or Percentage
        if sort_by == "sgpa":
            filtered.sort(key=lambda x: x["sgpa"], reverse=not ascending)
        else:
            filtered.sort(key=lambda x: x["percentage"], reverse=not ascending)
        
        # Assign ranks
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
        """Get available filter options"""
        if not self._loaded:
            self.load_data()
        
        branches = [
            {"code": code, "short": info["code"], "name": info["name"]}
            for code, info in BRANCHES.items()
        ]
        
        semesters = sorted(set(s["semester"] for s in self.students if s["semester"]))
        batches = sorted(set(s["batch"] for s in self.students if s["batch"]), reverse=True)
        
        return {
            "branches": branches,
            "semesters": semesters,
            "batches": batches
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