document.addEventListener('DOMContentLoaded', function() {
    // CSRF Token Helper
    function getCSRFToken() {
        return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }

    // Timetable Form
    const timetableForm = document.getElementById('timetableForm');
    if (timetableForm) {
        timetableForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const classroom = this.classroom.value;
            fetch(`/accounts/student/timetable/?classroom=${encodeURIComponent(classroom)}`)
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.length) {
                        html = '<table class="w-full"><tr><th>Day</th><th>Start</th><th>End</th><th>Teacher</th></tr>';
                        data.forEach(d => {
                            html += `<tr><td>${d.day}</td><td>${d.start_time}</td><td>${d.end_time}</td><td>${d.teacher}</td></tr>`;
                        });
                        html += '</table>';
                    } else {
                        html = '<p class="text-red-500">No timetable found.</p>';
                    }
                    document.getElementById('timetableResults').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('timetableResults').innerHTML = '<p class="text-red-500">Error fetching timetable.</p>';
                });
        });
    }

    // Availability Form
    const availabilityForm = document.getElementById('availabilityForm');
    if (availabilityForm) {
        availabilityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const params = new URLSearchParams(new FormData(this)).toString();
            fetch(`/accounts/student/available-classrooms/?${params}`)
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.length) {
                        html = '<table class="w-full"><tr><th>Classroom</th><th>Block</th></tr>';
                        data.forEach(d => {
                            html += `<tr><td>${d.name}</td><td>${d.block}</td></tr>`;
                        });
                        html += '</table>';
                    } else {
                        html = '<p class="text-red-500">No available classrooms.</p>';
                    }
                    document.getElementById('availabilityResults').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('availabilityResults').innerHTML = '<p class="text-red-500">Error fetching availability.</p>';
                });
        });
    }

    // Admin Dashboard Functions
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch('/admin-dashboard/upload-timetable/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('uploadStatus').innerHTML = `<p>${data.message}</p>`;
                if (data.errors) {
                    data.errors.forEach(error => {
                        document.getElementById('uploadStatus').innerHTML += `<p class="text-red-500">${error}</p>`;
                    });
                }
                loadTimetable();
            })
            .catch(error => {
                document.getElementById('uploadStatus').innerHTML = '<p class="text-red-500">Upload failed</p>';
            });
        });
    }

    function initCharts() {
        if (document.getElementById('usageChart')) {
            fetch('/admin-dashboard/usage/')
                .then(res => res.json())
                .then(data => {
                    new Chart(document.getElementById('usageChart'), {
                        type: 'bar',
                        data: {
                            labels: data.labels,
                            datasets: [{ label: 'Bookings Count', data: data.data, backgroundColor: '#ADD8E6' }]
                        }
                    });
                });
            fetch('/admin-dashboard/peak-hours/')
                .then(res => res.json())
                .then(data => {
                    new Chart(document.getElementById('peakHoursChart'), {
                        type: 'line',
                        data: {
                            labels: data.labels,
                            datasets: [{ label: 'Bookings per Hour', data: data.data, borderColor: '#007bff', fill: false }]
                        }
                    });
                });
            fetch('/admin-dashboard/active-faculty/')
                .then(res => res.json())
                .then(data => {
                    new Chart(document.getElementById('activeFacultyChart'), {
                        type: 'pie',
                        data: {
                            labels: data.labels,
                            datasets: [{ data: data.data, backgroundColor: ['#4CAF50', '#007bff', '#ffc107', '#f44336'] }]
                        }
                    });
                });
        }
    }

    const adminAvailabilityForm = document.getElementById('availabilityForm');
    if (adminAvailabilityForm) {
        adminAvailabilityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const params = new URLSearchParams(formData).toString();
            fetch(`/admin-dashboard/available-classrooms/?${params}`)
                .then(res => res.json())
                .then(data => {
                    const tbody = document.querySelector('#availabilityTable tbody');
                    tbody.innerHTML = data.map(i => `<tr><td>${i.name}</td><td>${i.block}</td></tr>`).join('');
                    document.getElementById('availabilityTable').style.display = 'table';
                })
                .catch(() => Swal.fire('Error', 'Could not fetch availability data', 'error'));
        });
    }

    function loadPendingBookings() {
        if (document.getElementById('bookingTable')) {
            fetch('/admin-dashboard/pending-bookings/')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.querySelector('#bookingTable tbody');
                    tbody.innerHTML = data.map(b => `
                        <tr>
                            <td>${b.user}</td>
                            <td>${b.classroom}</td>
                            <td>${b.date}</td>
                            <td>${b.start_time} - ${b.end_time}</td>
                            <td class="form-group flex gap-2">
                                <button class="approve" onclick="handleBookingAction(${b.id}, 'approve')">Approve</button>
                                <button class="reject" onclick="handleBookingAction(${b.id}, 'reject')">Reject</button>
                            </td>
                        </tr>
                    `).join('');
                });
        }
    }

    window.handleBookingAction = function(id, action) {
        Swal.fire({
            title: `${action.charAt(0).toUpperCase() + action.slice(1)} this booking?`,
            icon: 'warning',
            showCancelButton: true
        }).then(result => {
            if (result.isConfirmed) {
                fetch(`/admin-dashboard/${action}-booking/${id}/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRFToken() }
                })
                .then(() => Swal.fire('Success', `Booking ${action}ed`, 'success'))
                .then(loadPendingBookings);
            }
        });
    };

    function loadTimetable() {
        if (document.getElementById('timetableTable')) {
            fetch('/admin-dashboard/timetable/')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.querySelector('#timetableTable tbody');
                    tbody.innerHTML = data.map(item => `
                        <tr data-id="${item.id}">
                            <td><input value="${item.day}" class="w-full p-1 border rounded"></td>
                            <td><input type="time" value="${item.start_time}" class="w-full p-1 border rounded"></td>
                            <td><input type="time" value="${item.end_time}" class="w-full p-1 border rounded"></td>
                            <td><input value="${item.classroom}" class="w-full p-1 border rounded"></td>
                            <td><input value="${item.teacher}" class="w-full p-1 border rounded"></td>
                            <td class="form-group flex gap-2">
                                <button class="edit" onclick="saveTimetable(${item.id})">Save</button>
                                <button class="delete" onclick="deleteTimetable(${item.id})">Delete</button>
                            </td>
                        </tr>
                    `).join('');
                    document.getElementById('timetableTable').style.display = 'table';
                    document.getElementById('timetableLoading').style.display = 'none';
                });
        }
    }

    window.saveTimetable = function(id) {
        const row = document.querySelector(`tr[data-id='${id}']`);
        const inputs = row.querySelectorAll('input');
        fetch(`/admin-dashboard/timetable/update/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                day: inputs[0].value,
                start_time: inputs[1].value,
                end_time: inputs[2].value,
                classroom: inputs[3].value,
                teacher: inputs[4].value
            })
        }).then(() => Swal.fire('Saved!', '', 'success')).then(loadTimetable);
    };

    window.deleteTimetable = function(id) {
        Swal.fire({
            title: 'Delete entry?',
            showCancelButton: true,
            confirmButtonText: 'Delete'
        }).then(result => {
            if (result.isConfirmed) {
                fetch(`/admin-dashboard/timetable/delete/${id}/`, {
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': getCSRFToken() }
                }).then(() => Swal.fire('Deleted!', '', 'success')).then(loadTimetable);
            }
        });
    };

    window.exportCSV = function() {
        window.location.href = '/admin-dashboard/timetable/export/';
    };

    // Initialize Dashboard Components
    initCharts();
    loadPendingBookings();
    loadTimetable();
});
