let allCourses = [];

async function init() {
    allCourses = await (await fetch('/api/courses')).json();
    renderCourses(allCourses);
}

function renderCourses(filtered) {
    document.getElementById('coursesList').innerHTML = filtered.map(c => `
        <label class="course-item">
            <input type="checkbox" value="${c.id}">
            <div>
                <strong>${c.id} - ${c.title}</strong>
                <div style="font-size:0.85em;color:#666;margin-top:4px">${c.desc}</div>
            </div>
        </label>
    `).join('');
}

function filterCourses() {
    const subject = document.getElementById('searchSubject').value.toLowerCase();
    const number = document.getElementById('searchNumber').value.toLowerCase();
    const title = document.getElementById('searchTitle').value.toLowerCase();
    renderCourses(allCourses.filter(c => {
        const s = c.id.replace(/\d+/, '').toLowerCase();
        const n = c.id.replace(/\D+/, '').toLowerCase();
        const t = c.title.toLowerCase();
        return (!subject || s.includes(subject)) && (!number || n.includes(number)) && (!title || t.includes(title));
    }));
}

async function buildSchedule() {
    const query = document.getElementById('query').value;
    if (!query) { alert('Enter what you are looking for'); return; }

    const completed = Array.from(document.querySelectorAll('.course-item input:checked')).map(x => x.value);
    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = '<p>Building schedules (this may take a moment)...</p>';

    const res = await fetch('/api/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            completed, query,
            major: document.getElementById('major').value,
            year: parseInt(document.getElementById('year').value),
            target_credits: parseInt(document.getElementById('targetCredits').value),
        })
    });

    const schedules = await res.json();
    if (!schedules.length) {
        resultsDiv.innerHTML = '<p>No valid schedules found. Try fewer constraints or a broader query.</p>';
        return;
    }

    resultsDiv.innerHTML = '<h2>Schedules</h2>' + schedules.map((s, i) => `
        <div class="result-item">
            <div><strong>Schedule ${i+1}</strong> — score: ${s.score.toFixed(2)}
                ${s.penalty > 0 ? `<span style="color:#c00"> (penalty: -${s.penalty.toFixed(2)})</span>` : ''}
            </div>
            <table style="margin-top:8px;border-collapse:collapse;width:100%">
                <thead><tr style="text-align:left;border-bottom:1px solid #ccc">
                    <th style="padding:4px 8px">Course</th>
                    <th style="padding:4px 8px">Title</th>
                    <th style="padding:4px 8px">Match</th>
                    <th style="padding:4px 8px">Credits</th>
                    <th style="padding:4px 8px">Section</th>
                    <th style="padding:4px 8px">Time</th>
                    <th style="padding:4px 8px">Instructor</th>
                </tr></thead>
                <tbody>${s.courses.map(c => `
                    <tr style="border-bottom:1px solid #eee">
                        <td style="padding:4px 8px"><strong>${c.id}</strong></td>
                        <td style="padding:4px 8px">${c.title}</td>
                        <td style="padding:4px 8px">${c.recommendation_score}</td>
                        <td style="padding:4px 8px">${c.credits}</td>
                        <td style="padding:4px 8px">${c.section}</td>
                        <td style="padding:4px 8px">${c.time}</td>
                        <td style="padding:4px 8px">${c.instructor}</td>
                    </tr>
                `).join('')}</tbody>
            </table>
        </div>
    `).join('');
}

function clearAll() {
    document.querySelectorAll('.course-item input').forEach(x => x.checked = false);
    ['query', 'searchSubject', 'searchNumber', 'searchTitle'].forEach(id => document.getElementById(id).value = '');
    renderCourses(allCourses);
    document.getElementById('results').style.display = 'none';
}

document.getElementById('searchSubject').addEventListener('input', filterCourses);
document.getElementById('searchNumber').addEventListener('input', filterCourses);
document.getElementById('searchTitle').addEventListener('input', filterCourses);

init();
