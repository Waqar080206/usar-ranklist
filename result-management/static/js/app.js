// USAR Ranklist - Frontend Logic

let currentData = [];

// Load filters when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 USAR Ranklist loaded');
    loadFilters();
});

// Filter by branch (from footer links)
function filterBranch(branch) {
    document.getElementById('branchSelect').value = branch;
    loadRanklist();
}

// Load filter options from API
async function loadFilters() {
    console.log('📥 Loading filters...');
    
    try {
        const response = await fetch('/api/filters');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Filters response:', data);
        
        populateFilters(data);
        
        // Update hero stats
        if (data.total_students) {
            document.getElementById('heroTotalStudents').textContent = data.total_students + '+';
        }
        
    } catch (error) {
        console.error('❌ API Error:', error);
        populateFilters(getDefaultFilters());
    }
}

// Get default filters (fallback)
function getDefaultFilters() {
    return {
        branches: [
            { code: "519", short: "AIDS", name: "Artificial Intelligence & Data Science" },
            { code: "516", short: "AIML", name: "Artificial Intelligence & Machine Learning" },
            { code: "520", short: "IIOT", name: "Industrial Internet of Things" },
            { code: "517", short: "AR", name: "Automation & Robotics" }
        ],
        semesters: ["01", "02", "03", "04", "05", "06", "07", "08"],
        batches: ["2024", "2023", "2022", "2021"]
    };
}

// Populate filter dropdowns
function populateFilters(data) {
    const branchSelect = document.getElementById('branchSelect');
    if (branchSelect) {
        branchSelect.innerHTML = '<option value="">All Branches</option>';
        const branches = data.branches || getDefaultFilters().branches;
        branches.forEach(branch => {
            const option = document.createElement('option');
            option.value = branch.short;
            option.textContent = `${branch.short} - ${branch.name}`;
            branchSelect.appendChild(option);
        });
    }
    
    const semesterSelect = document.getElementById('semesterSelect');
    if (semesterSelect) {
        semesterSelect.innerHTML = '<option value="">All</option>';
        const semesters = data.semesters || getDefaultFilters().semesters;
        semesters.forEach(sem => {
            const option = document.createElement('option');
            option.value = sem;
            option.textContent = `Sem ${parseInt(sem)}`;
            semesterSelect.appendChild(option);
        });
    }
    
    const batchSelect = document.getElementById('batchSelect');
    if (batchSelect) {
        batchSelect.innerHTML = '<option value="">All</option>';
        const batches = data.batches || getDefaultFilters().batches;
        batches.forEach(batch => {
            const option = document.createElement('option');
            option.value = batch;
            option.textContent = batch;
            batchSelect.appendChild(option);
        });
    }
    
    console.log('✅ Filters populated');
}

// Load ranklist based on filters
async function loadRanklist() {
    const branch = document.getElementById('branchSelect').value;
    const semester = document.getElementById('semesterSelect').value;
    const batch = document.getElementById('batchSelect').value;
    const sortBy = document.getElementById('sortSelect').value;
    const order = document.getElementById('orderSelect').value;
    
    let url = `/api/ranklist?sort_by=${sortBy}&order=${order}`;
    if (branch) url += `&branch=${branch}`;
    if (semester) url += `&semester=${semester}`;
    if (batch) url += `&batch=${batch}`;
    
    console.log('📥 Fetching:', url);
    
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Ranklist:', data.total, 'students');
        
        currentData = data.ranklist || [];
        displayRanklist(data);
        displayStats(data);
        
    } catch (error) {
        console.error('❌ Error:', error);
        alert('Failed to load ranklist');
    }
}

// Display ranklist in table
function displayRanklist(data) {
    const tbody = document.getElementById('ranklistBody');
    const ranklist = data.ranklist || [];
    
    // Update result count
    const resultCount = document.getElementById('resultCount');
    const resultCountNum = document.getElementById('resultCountNum');
    
    if (ranklist.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8">
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-search"></i>
                        </div>
                        <h5>No Results Found</h5>
                        <p>Try adjusting your filters to find students</p>
                    </div>
                </td>
            </tr>
        `;
        resultCount.style.display = 'none';
        document.getElementById('statsRow').style.display = 'none';
        return;
    }
    
    resultCount.style.display = 'inline-flex';
    resultCountNum.textContent = ranklist.length;
    
    tbody.innerHTML = ranklist.map(student => {
        const rankDisplay = student.rank === 1 ? '🥇' : 
                            student.rank === 2 ? '🥈' : 
                            student.rank === 3 ? '🥉' : student.rank;
        const rankClass = student.rank <= 3 ? `rank-${student.rank}` : '';
        
        const sgpa = typeof student.sgpa === 'number' ? student.sgpa.toFixed(2) : student.sgpa;
        const percentage = typeof student.percentage === 'number' ? student.percentage.toFixed(2) : student.percentage;
        
        return `
            <tr onclick="viewStudent('${student.roll_no}')">
                <td class="text-center">
                    <span class="rank-badge ${rankClass}">${rankDisplay}</span>
                </td>
                <td><span class="student-roll">${student.roll_no}</span></td>
                <td><span class="student-name">${student.name}</span></td>
                <td><span class="branch-badge branch-${student.branch}">${student.branch}</span></td>
                <td class="text-center">${parseInt(student.semester)}</td>
                <td class="text-center">${student.batch}</td>
                <td class="text-center"><span class="sgpa-badge">${sgpa}</span></td>
                <td class="text-center"><span class="percentage-badge">${percentage}%</span></td>
            </tr>
        `;
    }).join('');
}

// Display stats
function displayStats(data) {
    const ranklist = data.ranklist || [];
    
    if (ranklist.length === 0) {
        document.getElementById('statsRow').style.display = 'none';
        return;
    }
    
    const sgpas = ranklist.map(s => s.sgpa).filter(s => s > 0);
    const percentages = ranklist.map(s => s.percentage).filter(p => p > 0);
    
    const avgSgpa = sgpas.length > 0 ? (sgpas.reduce((a, b) => a + b, 0) / sgpas.length).toFixed(2) : '0.00';
    const avgPercentage = percentages.length > 0 ? (percentages.reduce((a, b) => a + b, 0) / percentages.length).toFixed(2) : '0.00';
    
    document.getElementById('statsRow').style.display = 'grid';
    document.getElementById('totalStudents').textContent = ranklist.length;
    document.getElementById('avgSgpa').textContent = avgSgpa;
    document.getElementById('avgPercentage').textContent = avgPercentage + '%';
    document.getElementById('topperName').textContent = ranklist[0] ? ranklist[0].name.split(' ')[0] : '-';
}

// View student details
async function viewStudent(rollNo) {
    try {
        const response = await fetch(`/api/student/${rollNo}`);
        
        if (!response.ok) {
            alert('Student not found');
            return;
        }
        
        const student = await response.json();
        
        const sgpa = typeof student.sgpa === 'number' ? student.sgpa.toFixed(2) : student.sgpa;
        const percentage = typeof student.percentage === 'number' ? student.percentage.toFixed(2) : student.percentage;
        
        document.getElementById('studentDetails').innerHTML = `
            <div class="text-center mb-4">
                <div style="width: 80px; height: 80px; background: var(--gradient-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 2rem; color: white;">
                    ${student.name.charAt(0)}
                </div>
                <h4 style="margin-bottom: 4px; font-weight: 700;">${student.name}</h4>
                <p style="color: var(--gray-500); font-family: monospace;">${student.roll_no}</p>
            </div>
            
            <div class="row g-3 mb-4">
                <div class="col-4">
                    <div style="background: var(--gray-50); padding: 1rem; border-radius: var(--radius); text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">${sgpa}</div>
                        <div style="font-size: 0.75rem; color: var(--gray-500);">SGPA</div>
                    </div>
                </div>
                <div class="col-4">
                    <div style="background: var(--gray-50); padding: 1rem; border-radius: var(--radius); text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--success);">${percentage}%</div>
                        <div style="font-size: 0.75rem; color: var(--gray-500);">Percentage</div>
                    </div>
                </div>
                <div class="col-4">
                    <div style="background: var(--gray-50); padding: 1rem; border-radius: var(--radius); text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--warning);">${student.credits || 0}</div>
                        <div style="font-size: 0.75rem; color: var(--gray-500);">Credits</div>
                    </div>
                </div>
            </div>
            
            <div style="background: var(--gray-50); padding: 1rem; border-radius: var(--radius);">
                <p style="margin-bottom: 8px;"><strong>Branch:</strong> ${student.branch_name || student.branch}</p>
                <p style="margin-bottom: 8px;"><strong>Semester:</strong> ${student.semester}</p>
                <p style="margin-bottom: 0;"><strong>Batch:</strong> ${student.batch}</p>
            </div>
        `;
        
        new bootstrap.Modal(document.getElementById('studentModal')).show();
        
    } catch (error) {
        console.error('❌ Error:', error);
        alert('Failed to load student details');
    }
}

// Export to CSV
function exportToCSV() {
    if (!currentData || currentData.length === 0) {
        alert('No data to export. Please load ranklist first.');
        return;
    }
    
    const headers = ['Rank', 'Roll No', 'Name', 'Branch', 'Semester', 'Batch', 'SGPA', 'Percentage'];
    const rows = currentData.map(s => [
        s.rank, s.roll_no, s.name, s.branch, s.semester, s.batch,
        typeof s.sgpa === 'number' ? s.sgpa.toFixed(2) : s.sgpa,
        typeof s.percentage === 'number' ? s.percentage.toFixed(2) : s.percentage
    ]);
    
    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
        csv += row.map(val => `"${val}"`).join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'USAR_Ranklist.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}