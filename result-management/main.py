# main.py
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional
from models import *
from database_service import db_service
import uvicorn

app = FastAPI(
    title="Student Results Management System",
    description="API for managing and viewing student results semester-wise and branch-wise",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await db_service.setup_indexes()

# ============ Student Endpoints ============

@app.post("/api/students", response_model=dict, tags=["Students"])
async def create_student(student: Student):
    """Create a new student record"""
    try:
        student_id = await db_service.create_student(student)
        return {"message": "Student created successfully", "id": student_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/students/{roll_number}", response_model=Student, tags=["Students"])
async def get_student(roll_number: str):
    """Get student details by roll number"""
    student = await db_service.get_student(roll_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/api/students/{roll_number}", tags=["Students"])
async def update_student(roll_number: str, update_data: dict):
    """Update student information"""
    success = await db_service.update_student(roll_number, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}

@app.post("/api/students/{roll_number}/results", tags=["Results"])
async def add_semester_result(roll_number: str, result: SemesterResult):
    """Add or update semester result for a student"""
    success = await db_service.add_semester_result(roll_number, result)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Result added successfully"}

# ============ Branch-wise Endpoints ============

@app.get("/api/branches", response_model=List[dict], tags=["Branches"])
async def get_all_branches():
    """Get list of all branches"""
    return [{"code": b.name, "name": b.value} for b in Branch]

@app.get("/api/branches/{branch}/students", response_model=List[Student], tags=["Branches"])
async def get_students_by_branch(
    branch: Branch,
    semester: Optional[int] = Query(None, ge=1, le=8),
    batch_year: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("roll_number", regex="^(roll_number|name|cgpa)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$")
):
    """Get all students in a branch with optional filters"""
    order = 1 if sort_order == "asc" else -1
    return await db_service.get_students_by_branch(
        branch, semester, batch_year, skip, limit, sort_by, order
    )

@app.get("/api/branches/{branch}/statistics", response_model=BranchStats, tags=["Branches"])
async def get_branch_statistics(
    branch: Branch,
    semester: Optional[int] = Query(None, ge=1, le=8)
):
    """Get statistics for a branch"""
    stats = await db_service.get_branch_statistics(branch, semester)
    if not stats:
        raise HTTPException(status_code=404, detail="No data found")
    return stats

@app.get("/api/branches/{branch}/toppers", response_model=List[StudentSummary], tags=["Branches"])
async def get_branch_toppers(
    branch: Branch,
    semester: Optional[int] = Query(None, ge=1, le=8),
    limit: int = Query(10, ge=1, le=50)
):
    """Get top performing students in a branch"""
    return await db_service.get_branch_toppers(branch, semester, limit)

@app.get("/api/branches/{branch}/semesters-summary", tags=["Branches"])
async def get_branch_semesters_summary(branch: Branch):
    """Get summary of all semesters for a branch"""
    return await db_service.get_all_semesters_summary(branch)

# ============ Semester-wise Endpoints ============

@app.get("/api/semesters/{semester}/students", response_model=List[Student], tags=["Semesters"])
async def get_students_by_semester(
    semester: int = Query(..., ge=1, le=8),
    branch: Optional[Branch] = None,
    batch_year: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all students in a semester with optional branch filter"""
    return await db_service.get_students_by_semester(
        semester, branch, batch_year, skip, limit
    )

@app.get("/api/semesters/{semester}/results", tags=["Semesters"])
async def get_semester_results(
    semester: int = Query(..., ge=1, le=8),
    branch: Branch = Query(...),
    batch_year: Optional[int] = None,
    sort_by_sgpa: bool = Query(True)
):
    """Get all results for a specific semester and branch"""
    return await db_service.get_semester_results(
        semester, branch, batch_year, sort_by_sgpa
    )

# ============ Search Endpoint ============

@app.get("/api/search", response_model=List[StudentSummary], tags=["Search"])
async def search_students(
    q: str = Query(..., min_length=2),
    branch: Optional[Branch] = None,
    semester: Optional[int] = Query(None, ge=1, le=8)
):
    """Search students by name or roll number"""
    return await db_service.search_students(q, branch, semester)

# ============ Bulk Operations ============

@app.post("/api/bulk/students", tags=["Bulk Operations"])
async def bulk_create_students(students: List[Student]):
    """Create multiple students at once"""
    created = 0
    errors = []
    for student in students:
        try:
            await db_service.create_student(student)
            created += 1
        except Exception as e:
            errors.append({"roll_number": student.roll_number, "error": str(e)})
    return {"created": created, "errors": errors}

@app.post("/api/bulk/results", tags=["Bulk Operations"])
async def bulk_add_results(results: List[dict]):
    """Add results for multiple students
    
    Expected format:
    [{"roll_number": "XXX", "result": SemesterResult}, ...]
    """
    added = 0
    errors = []
    for item in results:
        try:
            result = SemesterResult(**item["result"])
            success = await db_service.add_semester_result(item["roll_number"], result)
            if success:
                added += 1
            else:
                errors.append({"roll_number": item["roll_number"], "error": "Student not found"})
        except Exception as e:
            errors.append({"roll_number": item.get("roll_number", "unknown"), "error": str(e)})
    return {"added": added, "errors": errors}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)