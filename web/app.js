/* filepath: w:\usar-ranklist\web\app.js */
// Sample data
const students = [
    { rank: 1, name: "Aarav Sharma", enrollment: "04115003523", total: 892, max: 1000, percentage: 89.2, subjects: { "Mathematics": 95, "Physics": 88, "Chemistry": 92, "Programming": 90, "Electronics": 87 } },
    { rank: 2, name: "Priya Singh", enrollment: "04115003524", total: 875, max: 1000, percentage: 87.5, subjects: { "Mathematics": 92, "Physics": 85, "Chemistry": 89, "Programming": 88, "Electronics": 86 } },
    { rank: 3, name: "Rohan Gupta", enrollment: "04115003525", total: 856, max: 1000, percentage: 85.6, subjects: { "Mathematics": 88, "Physics": 84, "Chemistry": 86, "Programming": 85, "Electronics": 83 } },
    { rank: 4, name: "Ananya Patel", enrollment: "04115003526", total: 834, max: 1000, percentage: 83.4, subjects: { "Mathematics": 85, "Physics": 82, "Chemistry": 84, "Programming": 83, "Electronics": 80 } },
    { rank: 5, name: "Vikram Reddy", enrollment: "04115003527", total: 812, max: 1000, percentage: 81.2, subjects: { "Mathematics": 82, "Physics": 80, "Chemistry": 81, "Programming": 79, "Electronics": 78 } },
];

// Elements
const searchInput = document.getElementById('search-input');
const sortSelect = document.getElementById('sort-select');
const tbody = document.getElementById('results-tbody');
const modal = document.getElementById('modal');
const closeModal = document.getElementById('close-modal');

// Init
document.addEventListener('DOMContentLoaded', () => {
    updateStats();
    renderTable(students);
    
    searchInput.addEventListener('input', handleFilter);
    sortSelect.addEventListener('change', handleFilter);
    closeModal.addEventListener('click', () => modal.classList.remove('active'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });
});

function updateStats() {
    document.getElementById('total-students').textContent = students.length;
    document.getElementById('top-percentage').textContent = Math.max(...students.map(s => s.percentage)).toFixed(1) + '%';
    const avg = students.reduce((a, s) => a + s.percentage, 0) / students.length;
    document.getElementById('avg-percentage').textContent = avg.toFixed(1) + '%';
}

function handleFilter() {
    const query = searchInput.value.toLowerCase();
    let filtered = students.filter(s => 
        s.name.toLowerCase().includes(query) || 
        s.enrollment.includes(query)
    );
    
    const sortBy = sortSelect.value;
    if (sortBy === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name));
    else if (sortBy === 'percentage') filtered.sort((a, b) => b.percentage - a.percentage);
    else filtered.sort((a, b) => a.rank - b.rank);
    
    renderTable(filtered);
}

function renderTable(data) {
    if (data.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="5">No results found</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(s => `
        <tr onclick="showModal('${s.enrollment}')">
            <td class="rank-cell rank-${s.rank <= 3 ? s.rank : ''}">#${s.rank}</td>
            <td>${s.name}</td>
            <td>${s.enrollment}</td>
            <td>${s.total}/${s.max}</td>
            <td>${s.percentage}%</td>
        </tr>
    `).join('');
}

function showModal(enrollment) {
    const s = students.find(x => x.enrollment === enrollment);
    if (!s) return;
    
    document.getElementById('modal-avatar').textContent = s.name.split(' ').map(n => n[0]).join('');
    document.getElementById('modal-name').textContent = s.name;
    document.getElementById('modal-enrollment').textContent = s.enrollment;
    document.getElementById('modal-rank').textContent = '#' + s.rank;
    document.getElementById('modal-total').textContent = `${s.total}/${s.max}`;
    document.getElementById('modal-percentage').textContent = s.percentage + '%';
    
    document.getElementById('modal-subjects').innerHTML = `
        <h4>Subjects</h4>
        ${Object.entries(s.subjects).map(([name, marks]) => `
            <div class="subject-row">
                <span>${name}</span>
                <span>${marks}/100</span>
            </div>
        `).join('')}
    `;
    
    modal.classList.add('active');
}