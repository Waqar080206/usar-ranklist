"""
USAR Ranklist - Simplified Branch-wise Ranking System
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional
from pathlib import Path

from database_service import data_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Loading student data...")
    data_service.load_data()
    print(f"✅ Loaded {len(data_service.students)} students")
    yield
    print("👋 Server stopped")


app = FastAPI(title="USAR Ranklist", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ============ Main Page ============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main ranklist page"""
    filters = data_service.get_filter_options()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "branches": filters["branches"],
        "semesters": filters["semesters"],
        "batches": filters["batches"]
    })


# ============ API ============

@app.get("/api/ranklist")
async def get_ranklist(
    branch: Optional[str] = Query(None, description="Branch: AIDS, AIML, IIOT, AR"),
    semester: Optional[str] = Query(None, description="Semester: 01, 02, 03..."),
    batch: Optional[str] = Query(None, description="Batch: 2024, 2023..."),
    sort_by: str = Query("sgpa", description="Sort by: sgpa, percentage"),
    order: str = Query("desc", description="Order: asc, desc")
):
    """
    Get branch-wise ranklist
    - Sorted by SGPA or Percentage
    - Ascending or Descending order
    """
    return data_service.get_ranklist(
        branch=branch,
        semester=semester,
        batch=batch,
        sort_by=sort_by,
        ascending=(order == "asc")
    )


@app.get("/api/filters")
async def get_filters():
    """Get available filter options"""
    return data_service.get_filter_options()


@app.get("/api/student/{roll_no}")
async def get_student(roll_no: str):
    """Get student details"""
    return data_service.get_student_by_roll(roll_no)


@app.get("/api/stats")
async def get_stats(
    branch: Optional[str] = None,
    semester: Optional[str] = None,
    batch: Optional[str] = None
):
    """Get statistics for selected filters"""
    return data_service.get_stats(branch, semester, batch)


if __name__ == "__main__":
    import uvicorn
    print("\n🎓 USAR RANKLIST SERVER")
    print("📍 http://localhost:8000\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)