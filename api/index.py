"""
USAR Ranklist - Vercel Serverless API
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Embedded student data - will be loaded from file
STUDENTS = []

def load_students():
    global STUDENTS
    if STUDENTS:
        return STUDENTS
    
    try:
        # Try importing from same directory
        from api.embedded_data import STUDENT_DATA
        STUDENTS = STUDENT_DATA
        return STUDENTS
    except:
        pass
    
    try:
        from embedded_data import STUDENT_DATA
        STUDENTS = STUDENT_DATA
        return STUDENTS
    except:
        pass
    
    return []

# Branch mapping
BRANCH_MAP = {
    "519": {"short": "AIDS", "name": "Artificial Intelligence & Data Science"},
    "516": {"short": "AIML", "name": "Artificial Intelligence & Machine Learning"},
    "520": {"short": "IIOT", "name": "Industrial Internet of Things"},
    "517": {"short": "AR", "name": "Automation & Robotics"},
}

def get_branch_from_roll(roll_no: str) -> dict:
    if len(roll_no) >= 5:
        code = roll_no[6:9]
        return BRANCH_MAP.get(code, {"short": "UNK", "name": "Unknown"})
    return {"short": "UNK", "name": "Unknown"}

def calculate_sgpa(student: dict) -> float:
    subjects = student.get("subjects", [])
    if not subjects:
        return 0.0
    
    total_credits = 0
    total_points = 0
    grade_points = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "D": 3, "F": 0, "AB": 0}
    
    for subj in subjects:
        credits = subj.get("credits", 0) or 0
        grade = subj.get("grade", "F")
        points = grade_points.get(grade, 0)
        total_credits += credits
        total_points += credits * points
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0


@app.get("/api/health")
def health():
    students = load_students()
    return {"status": "ok", "students": len(students)}


@app.get("/api/filters")
def get_filters():
    students = load_students()
    semesters = sorted(set(s.get("semester", "") for s in students if s.get("semester")))
    batches = sorted(set(s.get("batch", "") for s in students if s.get("batch")), reverse=True)
    
    return {
        "branches": [
            {"code": "519", "short": "AIDS", "name": "Artificial Intelligence & Data Science"},
            {"code": "516", "short": "AIML", "name": "Artificial Intelligence & Machine Learning"},
            {"code": "520", "short": "IIOT", "name": "Industrial Internet of Things"},
            {"code": "517", "short": "AR", "name": "Automation & Robotics"},
        ],
        "semesters": semesters if semesters else ["01", "02", "03", "04", "05", "06", "07", "08"],
        "batches": batches if batches else ["2024", "2023", "2022", "2021"],
        "total_students": len(students)
    }


@app.get("/api/ranklist")
def get_ranklist(branch: str = None, semester: str = None, batch: str = None, sort_by: str = "sgpa", order: str = "desc"):
    students = load_students()
    filtered = students.copy()
    
    if branch:
        branch_codes = {v["short"]: k for k, v in BRANCH_MAP.items()}
        code = branch_codes.get(branch.upper())
        if code:
            filtered = [s for s in filtered if len(s.get("roll_no", "")) >= 5 and s["roll_no"][6:9] == code]
    
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
    results.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    for i, student in enumerate(results, 1):
        student["rank"] = i
    
    return {"total": len(results), "ranklist": results}


@app.get("/api/student/{roll_no}")
def get_student(roll_no: str):
    students = load_students()
    for student in students:
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


@app.get("/")
def home():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USAR Ranklist</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root{--primary:#6366f1;--primary-dark:#4f46e5;--success:#10b981;--warning:#f59e0b;--gray-50:#f8fafc;--gray-100:#f1f5f9;--gray-200:#e2e8f0;--gray-400:#94a3b8;--gray-500:#64748b;--gray-600:#475569;--gray-800:#1e293b;--gray-900:#0f172a;--bg-primary:#f8fafc;--bg-card:#fff;--gradient-primary:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);--gradient-dark:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);--shadow-lg:0 10px 15px -3px rgb(0 0 0/0.1);--radius:10px;--radius-lg:16px;--transition:all .3s ease}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Inter',sans-serif;background:var(--bg-primary);color:var(--gray-800);line-height:1.6;min-height:100vh;display:flex;flex-direction:column}
        .navbar-custom{background:var(--bg-card);padding:1rem 0;position:sticky;top:0;z-index:1000;box-shadow:var(--shadow-lg);border-bottom:1px solid var(--gray-100)}
        .navbar-custom .container{display:flex;justify-content:space-between;align-items:center}
        .navbar-brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--gray-900)}
        .brand-icon{width:44px;height:44px;background:var(--gradient-primary);border-radius:var(--radius);display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.25rem}
        .brand-name{font-weight:700;font-size:1.25rem}
        .hero-section{background:var(--gradient-primary);padding:4rem 0 6rem;position:relative;text-align:center;color:#fff}
        .hero-title{font-size:3rem;font-weight:800;margin-bottom:1rem}
        .hero-subtitle{font-size:1.125rem;opacity:.9;margin-bottom:2rem}
        .main-content{flex:1;padding:2rem 0;margin-top:-2rem;position:relative;z-index:10}
        .filter-card,.table-card{background:var(--bg-card);border-radius:var(--radius-lg);box-shadow:var(--shadow-lg);overflow:hidden;margin-bottom:2rem}
        .filter-header,.table-header{display:flex;align-items:center;gap:1rem;padding:1.25rem 1.5rem;background:var(--gray-50);border-bottom:1px solid var(--gray-100)}
        .filter-icon{width:44px;height:44px;background:var(--gradient-primary);border-radius:var(--radius);display:flex;align-items:center;justify-content:center;color:#fff}
        .filter-title{font-size:1.125rem;font-weight:600;margin:0}
        .filter-body{padding:1.5rem}
        .filter-select{width:100%;padding:.75rem 1rem;font-size:.9rem;background:var(--gray-50);border:2px solid var(--gray-200);border-radius:var(--radius);cursor:pointer}
        .filter-select:focus{outline:none;border-color:var(--primary)}
        .btn-search{display:flex;align-items:center;justify-content:center;gap:8px;padding:.75rem 1.5rem;background:var(--gradient-primary);color:#fff;border:none;border-radius:var(--radius);font-weight:600;cursor:pointer;transition:var(--transition)}
        .btn-search:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(99,102,241,.4)}
        .ranklist-table{width:100%;border-collapse:collapse}
        .ranklist-table th{padding:1rem;text-align:left;font-size:.75rem;font-weight:600;color:var(--gray-500);text-transform:uppercase;background:var(--gray-50);border-bottom:1px solid var(--gray-200)}
        .ranklist-table td{padding:1rem;font-size:.9rem;border-bottom:1px solid var(--gray-100)}
        .ranklist-table tbody tr{cursor:pointer;transition:var(--transition)}
        .ranklist-table tbody tr:hover{background:var(--gray-50)}
        .rank-badge{display:inline-flex;align-items:center;justify-content:center;min-width:36px;height:36px;padding:0 8px;border-radius:var(--radius);font-weight:700;background:var(--gray-100);color:var(--gray-600)}
        .rank-1{background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#fff}
        .rank-2{background:linear-gradient(135deg,#94a3b8,#64748b);color:#fff}
        .rank-3{background:linear-gradient(135deg,#f97316,#ea580c);color:#fff}
        .branch-badge{display:inline-flex;padding:4px 10px;border-radius:50px;font-size:.75rem;font-weight:600}
        .branch-AIDS{background:#dbeafe;color:#1d4ed8}
        .branch-AIML{background:#fce7f3;color:#be185d}
        .branch-IIOT{background:#cffafe;color:#0891b2}
        .branch-AR{background:#dcfce7;color:#15803d}
        .sgpa-badge{padding:6px 12px;background:linear-gradient(135deg,#dcfce7,#bbf7d0);color:#15803d;border-radius:var(--radius);font-weight:700}
        .percentage-badge{padding:6px 12px;background:linear-gradient(135deg,#e0e7ff,#c7d2fe);color:#4338ca;border-radius:var(--radius);font-weight:700}
        .empty-state{padding:4rem 2rem;text-align:center}
        .empty-icon{width:80px;height:80px;margin:0 auto 1.5rem;background:var(--gray-100);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;color:var(--gray-400)}
        .footer{background:var(--gradient-dark);color:#fff;padding:2rem 0;text-align:center;margin-top:auto}
        .stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}
        .stat-card{background:var(--bg-card);border-radius:var(--radius-lg);padding:1.5rem;display:flex;align-items:center;gap:1rem;box-shadow:var(--shadow-lg)}
        .stat-icon{width:56px;height:56px;border-radius:var(--radius);display:flex;align-items:center;justify-content:center;font-size:1.5rem;color:#fff}
        .stat-primary .stat-icon{background:var(--gradient-primary)}
        .stat-success .stat-icon{background:linear-gradient(135deg,#10b981,#059669)}
        .stat-warning .stat-icon{background:linear-gradient(135deg,#f59e0b,#d97706)}
        .stat-purple .stat-icon{background:linear-gradient(135deg,#8b5cf6,#7c3aed)}
        .stat-value{font-size:1.5rem;font-weight:700}
        .stat-label{font-size:.8rem;color:var(--gray-500)}
        @media(max-width:768px){.hero-title{font-size:2rem}.stats-grid{grid-template-columns:1fr}}
    </style>
</head>
<body>
    <nav class="navbar-custom">
        <div class="container">
            <a class="navbar-brand" href="/"><div class="brand-icon"><i class="fas fa-graduation-cap"></i></div><span class="brand-name">USAR Ranklist</span></a>
            <a href="https://github.com/Waqar080206/usar-ranklist" target="_blank" style="color:var(--gray-600);font-size:1.5rem"><i class="fab fa-github"></i></a>
        </div>
    </nav>
    <section class="hero-section">
        <div class="container">
            <h1 class="hero-title">Student Ranklist</h1>
            <p class="hero-subtitle">University School of Automation & Robotics, GGSIPU</p>
        </div>
    </section>
    <main class="main-content">
        <div class="container">
            <div class="filter-card">
                <div class="filter-header"><div class="filter-icon"><i class="fas fa-sliders-h"></i></div><h5 class="filter-title">Filter Students</h5></div>
                <div class="filter-body">
                    <div class="row g-3">
                        <div class="col-md-3"><label class="form-label small fw-bold">Branch</label><select class="filter-select" id="branchSelect"><option value="">All Branches</option></select></div>
                        <div class="col-md-2"><label class="form-label small fw-bold">Semester</label><select class="filter-select" id="semesterSelect"><option value="">All</option></select></div>
                        <div class="col-md-2"><label class="form-label small fw-bold">Batch</label><select class="filter-select" id="batchSelect"><option value="">All</option></select></div>
                        <div class="col-md-2"><label class="form-label small fw-bold">Sort By</label><select class="filter-select" id="sortSelect"><option value="sgpa">SGPA</option><option value="percentage">Percentage</option></select></div>
                        <div class="col-md-1"><label class="form-label small fw-bold">Order</label><select class="filter-select" id="orderSelect"><option value="desc">↓ High</option><option value="asc">↑ Low</option></select></div>
                        <div class="col-md-2 d-flex align-items-end"><button class="btn-search w-100" onclick="loadRanklist()"><i class="fas fa-search"></i> Search</button></div>
                    </div>
                </div>
            </div>
            <div class="stats-grid" id="statsRow" style="display:none">
                <div class="stat-card stat-primary"><div class="stat-icon"><i class="fas fa-users"></i></div><div><span class="stat-value" id="totalStudents">0</span><br><span class="stat-label">Students</span></div></div>
                <div class="stat-card stat-success"><div class="stat-icon"><i class="fas fa-chart-line"></i></div><div><span class="stat-value" id="avgSgpa">0</span><br><span class="stat-label">Avg SGPA</span></div></div>
                <div class="stat-card stat-warning"><div class="stat-icon"><i class="fas fa-percent"></i></div><div><span class="stat-value" id="avgPercentage">0%</span><br><span class="stat-label">Avg %</span></div></div>
                <div class="stat-card stat-purple"><div class="stat-icon"><i class="fas fa-trophy"></i></div><div><span class="stat-value" id="topperName">-</span><br><span class="stat-label">Topper</span></div></div>
            </div>
            <div class="table-card">
                <div class="table-header"><i class="fas fa-list-ol" style="color:var(--primary)"></i><span class="filter-title">Ranklist</span></div>
                <div class="table-responsive">
                    <table class="ranklist-table">
                        <thead><tr><th>Rank</th><th>Roll No</th><th>Name</th><th>Branch</th><th>Sem</th><th>Batch</th><th>SGPA</th><th>%</th></tr></thead>
                        <tbody id="ranklistBody"><tr><td colspan="8"><div class="empty-state"><div class="empty-icon"><i class="fas fa-search"></i></div><h5>Ready to Search</h5><p>Select filters and click Search</p></div></td></tr></tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>
    <footer class="footer"><p>Made with ❤️ for USAR Students | © 2024-2026</p></footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentData=[];
        document.addEventListener('DOMContentLoaded',()=>{console.log('🚀 Loaded');loadFilters()});
        async function loadFilters(){
            try{
                const r=await fetch('/api/filters');
                if(!r.ok)throw new Error('HTTP '+r.status);
                const d=await r.json();
                console.log('✅ Filters:',d);
                populateFilters(d);
            }catch(e){
                console.error('❌',e);
                populateFilters({branches:[{short:'AIDS',name:'AI & DS'},{short:'AIML',name:'AI & ML'},{short:'IIOT',name:'IIoT'},{short:'AR',name:'A&R'}],semesters:['01','02','03','04','05','06','07','08'],batches:['2024','2023','2022','2021']});
            }
        }
        function populateFilters(d){
            const b=document.getElementById('branchSelect'),s=document.getElementById('semesterSelect'),bt=document.getElementById('batchSelect');
            b.innerHTML='<option value="">All Branches</option>';
            (d.branches||[]).forEach(x=>{b.innerHTML+=`<option value="${x.short}">${x.short} - ${x.name}</option>`});
            s.innerHTML='<option value="">All</option>';
            (d.semesters||[]).forEach(x=>{s.innerHTML+=`<option value="${x}">Sem ${parseInt(x)}</option>`});
            bt.innerHTML='<option value="">All</option>';
            (d.batches||[]).forEach(x=>{bt.innerHTML+=`<option value="${x}">${x}</option>`});
        }
        async function loadRanklist(){
            const branch=document.getElementById('branchSelect').value,sem=document.getElementById('semesterSelect').value,batch=document.getElementById('batchSelect').value,sort=document.getElementById('sortSelect').value,order=document.getElementById('orderSelect').value;
            let url=`/api/ranklist?sort_by=${sort}&order=${order}`;
            if(branch)url+=`&branch=${branch}`;if(sem)url+=`&semester=${sem}`;if(batch)url+=`&batch=${batch}`;
            console.log('📥',url);
            try{
                const r=await fetch(url);if(!r.ok)throw new Error('HTTP '+r.status);
                const d=await r.json();console.log('✅',d.total,'students');
                currentData=d.ranklist||[];displayRanklist(d);displayStats(d);
            }catch(e){console.error('❌',e);alert('Failed to load');}
        }
        function displayRanklist(d){
            const tbody=document.getElementById('ranklistBody'),list=d.ranklist||[];
            if(!list.length){tbody.innerHTML='<tr><td colspan="8"><div class="empty-state"><div class="empty-icon"><i class="fas fa-search"></i></div><h5>No Results</h5></div></td></tr>';document.getElementById('statsRow').style.display='none';return;}
            tbody.innerHTML=list.map(s=>{
                const rank=s.rank===1?'🥇':s.rank===2?'🥈':s.rank===3?'🥉':s.rank;
                const rc=s.rank<=3?'rank-'+s.rank:'';
                return`<tr><td><span class="rank-badge ${rc}">${rank}</span></td><td>${s.roll_no}</td><td><strong>${s.name}</strong></td><td><span class="branch-badge branch-${s.branch}">${s.branch}</span></td><td>${parseInt(s.semester)}</td><td>${s.batch}</td><td><span class="sgpa-badge">${s.sgpa.toFixed(2)}</span></td><td><span class="percentage-badge">${s.percentage.toFixed(2)}%</span></td></tr>`;
            }).join('');
        }
        function displayStats(d){
            const list=d.ranklist||[];if(!list.length){document.getElementById('statsRow').style.display='none';return;}
            const sgpas=list.map(s=>s.sgpa).filter(s=>s>0),pcts=list.map(s=>s.percentage).filter(p=>p>0);
            document.getElementById('statsRow').style.display='grid';
            document.getElementById('totalStudents').textContent=list.length;
            document.getElementById('avgSgpa').textContent=sgpas.length?(sgpas.reduce((a,b)=>a+b,0)/sgpas.length).toFixed(2):'0';
            document.getElementById('avgPercentage').textContent=(pcts.length?(pcts.reduce((a,b)=>a+b,0)/pcts.length).toFixed(2):'0')+'%';
            document.getElementById('topperName').textContent=list[0]?list[0].name.split(' ')[0]:'-';
        }
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)