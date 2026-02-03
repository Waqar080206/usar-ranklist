"""
USAR Ranklist - Main Server
FastAPI application for student ranklist
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Optional

from database_service import data_service

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Initialize FastAPI
app = FastAPI(
    title="USAR Ranklist",
    description="Student Ranklist for USAR, GGSIPU",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = BASE_DIR / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    print(f"✅ Static files mounted from: {static_path}")
else:
    print(f"⚠️ Static folder not found at: {static_path}")

# Templates
templates_path = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_path))
print(f"✅ Templates loaded from: {templates_path}")


@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    print("🚀 Loading student data...")
    data_service.load_data()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main page"""
    filters = data_service.get_filter_options()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "branches": filters["branches"],
        "semesters": filters["semesters"],
        "batches": filters["batches"]
    })


@app.get("/api/filters")
async def get_filters():
    """Get available filter options"""
    return data_service.get_filter_options()


@app.get("/api/ranklist")
async def get_ranklist(
    branch: Optional[str] = None,
    semester: Optional[str] = None,
    batch: Optional[str] = None,
    sort_by: str = "sgpa",
    order: str = "desc"
):
    """Get ranklist with filters"""
    ascending = order.lower() == "asc"
    return data_service.get_ranklist(
        branch=branch,
        semester=semester,
        batch=batch,
        sort_by=sort_by,
        ascending=ascending
    )


@app.get("/api/student/{roll_no}")
async def get_student(roll_no: str):
    """Get student details by roll number"""
    student = data_service.get_student_by_roll(roll_no)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/api/stats")
async def get_stats(
    branch: Optional[str] = None,
    semester: Optional[str] = None,
    batch: Optional[str] = None
):
    """Get statistics"""
    return data_service.get_stats(branch, semester, batch)


# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "base_dir": str(BASE_DIR),
        "static_exists": (BASE_DIR / "static").exists(),
        "templates_exists": (BASE_DIR / "templates").exists(),
        "data_loaded": len(data_service.students) > 0,
        "total_students": len(data_service.students)
    }


if __name__ == "__main__":
    import uvicorn
    print("\n🎓 USAR RANKLIST SERVER")
    print("📍 http://localhost:8000\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)