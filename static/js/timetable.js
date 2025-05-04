document.addEventListener('DOMContentLoaded', function() {
    const timetableForm = document.getElementById('timetableForm');
    if (timetableForm) {
        timetableForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const classroom = this.classroom.value;
            fetch(`/public/timetable/?classroom=${encodeURIComponent(classroom)}`)
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.error) {
                        html = `<p class="text-red-500">${data.error}</p>`;
                    } else if (data.length) {
                        html = '<table class="w-full"><thead><tr><th>Day</th><th>Start</th><th>End</th><th>Teacher</th></tr></thead><tbody>';
                        data.forEach(d => {
                            html += `<tr><td>${d.day}</td><td>${d.start_time}</td><td>${d.end_time}</td><td>${d.teacher}</td></tr>`;
                        });
                        html += '</tbody></table>';
                    } else {
                        html = '<p class="text-red-500">No timetable found.</p>';
                    }
                    document.getElementById('timetableResults').innerHTML = html;
                })
                .catch(error => {
                    Swal.fire('Error', 'Error fetching timetable.', 'error');
                });
        });
    }

    const availabilityForm = document.getElementById('availabilityForm');
    if (availabilityForm) {
        availabilityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const params = new URLSearchParams(new FormData(this)).toString();
            fetch(`/public/available-classrooms/?${params}`)
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.error) {
                        html = `<p class="text-red-500">${data.error}</p>`;
                    } else if (data.length) {
                        html = '<table class="w-full"><thead><tr><th>Classroom</th><th>Block</th></tr></thead><tbody>';
                        data.forEach(d => {
                            html += `<tr><td>${d.name}</td><td>${d.block}</td></tr>`;
                        });
                        html += '</tbody></table>';
                    } else {
                        html = '<p class="text-red-500">No available classrooms.</p>';
                    }
                    document.getElementById('availabilityResults').innerHTML = html;
                })
                .catch(error => {
                    Swal.fire('Error', 'Error fetching availability.', 'error');
                });
        });
    }

    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const timetableForm = document.getElementById('timetableForm');
            if (query) {
                timetableForm.classroom.value = query;
                timetableForm.dispatchEvent(new Event('submit'));
            }
        });
    }
});
