"""
USAR Ranklist - FastAPI Backend
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

app = FastAPI(title="USAR Ranklist", version="1.0.0")

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent

# Load student data
def load_data():
    """Load student data from embedded_data.py or JSON file"""
    try:
        from embedded_data import STUDENT_DATA
        print(f"✅ Loaded {len(STUDENT_DATA)} students from embedded_data.py")
        return STUDENT_DATA
    except Exception as e:
        print(f"⚠️ embedded_data.py failed: {e}")
        
    # Fallback to JSON
    json_paths = [
        BASE_DIR / "data" / "parsed_results.json",
        Path("/var/task/result-management/data/parsed_results.json"),
    ]
    
    for json_path in json_paths:
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Loaded {len(data)} students from {json_path}")
                return data
    
    print("❌ No data source found")
    return []

# Load data at startup
STUDENTS = load_data()

# Branch mapping
BRANCH_MAP = {
    "519": {"short": "AIDS", "name": "Artificial Intelligence & Data Science"},
    "516": {"short": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    "520": {"short": "IIOT", "name": "Industrial Internet of Things"},
    "517": {"short": "AR", "name": "Automation & Robotics"},
}

def get_branch_from_roll(roll_no: str) -> dict:
    """Extract branch info from roll number"""
    if len(roll_no) >= 5:
        code = roll_no[2:5]
        return BRANCH_MAP.get(code, {"short": "UNK", "name": "Unknown"})
    return {"short": "UNK", "name": "Unknown"}

def calculate_sgpa(student: dict) -> float:
    """Calculate SGPA from subjects"""
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
    
    if total_credits == 0:
        return 0.0
    
    return round(total_points / total_credits, 2)

# API Routes
@app.get("/api/filters")
async def get_filters():
    """Get available filter options"""
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
    """Get filtered and sorted ranklist"""
    filtered = STUDENTS.copy()
    
    # Filter by branch
    if branch:
        branch_codes = {v["short"]: k for k, v in BRANCH_MAP.items()}
        code = branch_codes.get(branch.upper())
        if code:
            filtered = [s for s in filtered if len(s.get("roll_no", "")) >= 5 and s["roll_no"][2:5] == code]
    
    # Filter by semester
    if semester:
        filtered = [s for s in filtered if s.get("semester") == semester]
    
    # Filter by batch
    if batch:
        filtered = [s for s in filtered if s.get("batch") == batch]
    
    # Calculate SGPA for each student
    results = []
    for student in filtered:
        sgpa = calculate_sgpa(student)
        branch_info = get_branch_from_roll(student.get("roll_no", ""))
        
        # Calculate percentage from marks
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
    
    # Sort
    reverse = order.lower() == "desc"
    if sort_by == "percentage":
        results.sort(key=lambda x: x["percentage"], reverse=reverse)
    else:
        results.sort(key=lambda x: x["sgpa"], reverse=reverse)
    
    # Add ranks
    for i, student in enumerate(results, 1):
        student["rank"] = i
    
    return {
        "total": len(results),
        "ranklist": results
    }

@app.get("/api/student/{roll_no}")
async def get_student(roll_no: str):
    """Get student details by roll number"""
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
                "sid": student.get("sid", ""),
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

# Serve HTML page
@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main HTML page"""
    template_path = BASE_DIR / "templates" / "index.html"
    
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    
    return HTMLResponse(content="<h1>USAR Ranklist</h1><p>Template not found</p>")

# Health check
@app.get("/api/health")
async def health():
    return {"status": "ok", "students": len(STUDENTS)}

# For Vercel
handler = app