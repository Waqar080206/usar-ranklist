"""
USAR Ranklist - Main Server
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Optional
import os

from database_service import data_service

# Get directory
BASE_DIR = Path(__file__).resolve().parent

# Initialize FastAPI
app = FastAPI(title="USAR Ranklist")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - mount with absolute path
static_path = BASE_DIR / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Explicit static file routes for Vercel
@app.get("/static/css/style.css")
async def get_css():
    css_path = BASE_DIR / "static" / "css" / "style.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS not found")


@app.get("/static/js/app.js")
async def get_js():
    js_path = BASE_DIR / "static" / "js" / "app.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS not found")


# Load data on startup
@app.on_event("startup")
async def startup():
    data_service.load_data()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/filters")
async def get_filters():
    """Get filter options"""
    return data_service.get_filter_options()


@app.get("/api/ranklist")
async def get_ranklist(
    branch: Optional[str] = None,
    semester: Optional[str] = None,
    batch: Optional[str] = None,
    sort_by: str = "sgpa",
    order: str = "desc"
):
    """Get ranklist"""
    ascending = order.lower() == "asc"
    return data_service.get_ranklist(branch, semester, batch, sort_by, ascending)


@app.get("/api/student/{roll_no}")
async def get_student(roll_no: str):
    """Get student details"""
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


@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "students": len(data_service.students),
        "data_loaded": data_service._loaded,
        "static_path": str(static_path),
        "static_exists": static_path.exists()
    }


# For Vercel
handler = app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)