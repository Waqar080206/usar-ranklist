// USAR Ranklist - Frontend Logic

let currentData = [];

// Load filters when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 USAR Ranklist loaded');
    loadFilters();
});

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
        
    } catch (error) {
        console.error('❌ API Error:', error);
        // Use hardcoded defaults
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
    // Populate Branch dropdown
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
        console.log(`✅ Branch options: ${branches.length}`);
    }
    
    // Populate Semester dropdown
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
        console.log(`✅ Semester options: ${semesters.length}`);
    }
    
    // Populate Batch dropdown
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
        console.log(`✅ Batch options: ${batches.length}`);
    }
    
    console.log('✅ All filters populated');
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
    
    if (ranklist.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-5">
                    <i class="fas fa-search fa-2x mb-2 d-block"></i>
                    No students found for selected filters
                </td>
            </tr>
        `;
        document.getElementById('statsRow').style.display = 'none';
        return;
    }
    
    tbody.innerHTML = ranklist.map(student => {
        const rankBadge = student.rank === 1 ? '🥇' : 
                          student.rank === 2 ? '🥈' : 
                          student.rank === 3 ? '🥉' : student.rank;
        const rankClass = student.rank <= 3 ? `rank-${student.rank}` : '';
        
        const sgpa = typeof student.sgpa === 'number' ? student.sgpa.toFixed(2) : student.sgpa;
        const percentage = typeof student.percentage === 'number' ? student.percentage.toFixed(2) : student.percentage;
        
        return `
            <tr onclick="viewStudent('${student.roll_no}')" style="cursor: pointer;">
                <td class="text-center">
                    <span class="rank-badge ${rankClass}">${rankBadge}</span>
                </td>
                <td><strong>${student.roll_no}</strong></td>
                <td>${student.name}</td>
                <td><span class="badge bg-${getBranchColor(student.branch)}">${student.branch}</span></td>
                <td class="text-center">${student.semester}</td>
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
    
    document.getElementById('statsRow').style.display = 'flex';
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
            <div class="text-center mb-3">
                <h4>${student.name}</h4>
                <p class="text-muted">${student.roll_no}</p>
            </div>
            <div class="row text-center mb-3">
                <div class="col-4">
                    <div class="p-2 bg-light rounded">
                        <h5 class="text-primary mb-0">${sgpa}</h5>
                        <small>SGPA</small>
                    </div>
                </div>
                <div class="col-4">
                    <div class="p-2 bg-light rounded">
                        <h5 class="text-success mb-0">${percentage}%</h5>
                        <small>Percentage</small>
                    </div>
                </div>
                <div class="col-4">
                    <div class="p-2 bg-light rounded">
                        <h5 class="text-info mb-0">${student.credits || 0}</h5>
                        <small>Credits</small>
                    </div>
                </div>
            </div>
            <hr>
            <p><strong>Branch:</strong> ${student.branch_name || student.branch}</p>
            <p><strong>Semester:</strong> ${student.semester}</p>
            <p><strong>Batch:</strong> ${student.batch}</p>
        `;
        
        new bootstrap.Modal(document.getElementById('studentModal')).show();
        
    } catch (error) {
        console.error('❌ Error:', error);
        alert('Failed to load student details');
    }
}

// Get branch color
function getBranchColor(branch) {
    const colors = { 'AIDS': 'primary', 'AIML': 'danger', 'IIOT': 'info', 'AR': 'success' };
    return colors[branch] || 'secondary';
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