"""
USAR Ranklist - Vercel Serverless Function
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import sys
import os

# Add result-management to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'result-management'))

app = FastAPI(title="USAR Ranklist", version="1.0.0")

# Load student data
def load_data():
    """Load student data"""
    try:
        from embedded_data import STUDENT_DATA
        return STUDENT_DATA
    except:
        pass
    
    try:
        import embedded_data
        return embedded_data.STUDENT_DATA
    except:
        pass
    
    return []

STUDENTS = load_data()

# Branch mapping
BRANCH_MAP = {
    "519": {"short": "AIDS", "name": "Artificial Intelligence & Data Science"},
    "516": {"short": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    "520": {"short": "IIOT", "name": "Industrial Internet of Things"},
    "517": {"short": "AR", "name": "Automation & Robotics"},
}

def get_branch_from_roll(roll_no: str) -> dict:
    if len(roll_no) >= 5:
        code = roll_no[2:5]
        return BRANCH_MAP.get(code, {"short": "UNK", "name": "Unknown"})
    return {"short": "UNK", "name": "Unknown"}

def calculate_sgpa(student: dict) -> float:
    subjects = student.get("subjects", [])
    if not subjects:
        return 0.0
    
    total_credits = 0
    total_points = 0
    
    grade_points = {
        "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6,
        "C+": 5, "C": 4, "D": 3, "F": 0, "AB": 0
    }
    
    for subj in subjects:
        credits = subj.get("credits", 0) or 0
        grade = subj.get("grade", "F")
        points = grade_points.get(grade, 0)
        total_credits += credits
        total_points += credits * points
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0


@app.get("/api/health")
async def health():
    return {"status": "ok", "students": len(STUDENTS)}


@app.get("/api/filters")
async def get_filters():
    semesters = sorted(set(s.get("semester", "") for s in STUDENTS if s.get("semester")))
    batches = sorted(set(s.get("batch", "") for s in STUDENTS if s.get("batch")), reverse=True)
    
    branches = [
        {"code": "519", "short": "AIDS", "name": "Artificial Intelligence & Data Science"},
        {"code": "516", "short": "AIML", "name": "Artificial Intelligence & Machine Learning"},
        {"code": "520", "short": "IIOT", "name": "Industrial Internet of Things"},
        {"code": "517", "short": "AR", "name": "Automation & Robotics"},
    ]
    
    return {
        "branches": branches,
        "semesters": semesters,
        "batches": batches,
        "total_students": len(STUDENTS)
    }


@app.get("/api/ranklist")
async def get_ranklist(
    branch: str = None,
    semester: str = None,
    batch: str = None,
    sort_by: str = "sgpa",
    order: str = "desc"
):
    filtered = STUDENTS.copy()
    
    if branch:
        branch_codes = {v["short"]: k for k, v in BRANCH_MAP.items()}
        code = branch_codes.get(branch.upper())
        if code:
            filtered = [s for s in filtered if len(s.get("roll_no", "")) >= 5 and s["roll_no"][2:5] == code]
    
    if semester:
        filtered = [s for s in filtered if s.get("semester") == semester]
    
    if batch:
        filtered = [s for s in filtered if s.get("batch") == batch]
    
    results = []
    for student in filtered:
        sgpa = calculate_sgpa(student)
        branch_info = get_branch_from_roll(student.get("roll_no", ""))
        
        total = student.get("total_marks", 0) or 0
        max_marks = student.get("max_marks", 0) or 0
        percentage = round((total / max_marks * 100), 2) if max_marks > 0 else 0.0
        
        results.append({
            "roll_no": student.get("roll_no", ""),
            "name": student.get("name", ""),
            "branch": branch_info["short"],
            "branch_name": branch_info["name"],
            "semester": student.get("semester", ""),
            "batch": student.get("batch", ""),
            "sgpa": sgpa,
            "percentage": percentage,
            "credits": student.get("credits_secured", 0)
        })
    
    reverse = order.lower() == "desc"
    if sort_by == "percentage":
        results.sort(key=lambda x: x["percentage"], reverse=reverse)
    else:
        results.sort(key=lambda x: x["sgpa"], reverse=reverse)
    
    for i, student in enumerate(results, 1):
        student["rank"] = i
    
    return {"total": len(results), "ranklist": results}


@app.get("/api/student/{roll_no}")
async def get_student(roll_no: str):
    for student in STUDENTS:
        if student.get("roll_no") == roll_no:
            sgpa = calculate_sgpa(student)
            branch_info = get_branch_from_roll(roll_no)
            
            total = student.get("total_marks", 0) or 0
            max_marks = student.get("max_marks", 0) or 0
            percentage = round((total / max_marks * 100), 2) if max_marks > 0 else 0.0
            
            return {
                "roll_no": roll_no,
                "name": student.get("name", ""),
                "branch": branch_info["short"],
                "branch_name": branch_info["name"],
                "semester": student.get("semester", ""),
                "batch": student.get("batch", ""),
                "sgpa": sgpa,
                "percentage": percentage,
                "credits": student.get("credits_secured", 0),
                "subjects": student.get("subjects", [])
            }
    
    raise HTTPException(status_code=404, detail="Student not found")


@app.get("/", response_class=HTMLResponse)
async def home():
    import os
    template_path = os.path.join(os.path.dirname(__file__), '..', 'result-management', 'templates', 'index.html')
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    
    return HTMLResponse(content="<h1>USAR Ranklist</h1><p>Template not found</p>")


# Vercel handler
handler = app