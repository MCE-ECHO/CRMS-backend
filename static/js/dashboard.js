document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('uploadStatus').innerHTML = '<div class="loading">Uploading...</div>';
            const formData = new FormData(this);
            fetch('/admin-dashboard/upload-timetable/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                let statusHtml = `<p>${data.message}</p>`;
                if (data.errors) {
                    data.errors.forEach(error => {
                        statusHtml += `<p class="text-red-500">${error}</p>`;
                    });
                }
                document.getElementById('uploadStatus').innerHTML = statusHtml;
                loadTimetable();
                loadBookings();
                showAlert('Success', data.message);
            })
            .catch(error => {
                handleError(error, 'uploadStatus', 'Upload failed');
                showAlert('Error', 'Upload failed', 'error');
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
                            datasets: [{ label: 'Timetable Entries', data: data.data, backgroundColor: '#ADD8E6' }]
                        },
                        options: {
                            responsive: true,
                            scales: { y: { beginAtZero: true } }
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
                            datasets: [{ label: 'Timetable per Hour', data: data.data, borderColor: '#ADD8E6', fill: false }]
                        },
                        options: {
                            responsive: true,
                            scales: { y: { beginAtZero: true } }
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
                            datasets: [{ data: data.data, backgroundColor: ['#ADD8E6', '#FFD7BE', '#4CAF50', '#f44336'] }]
                        },
                        options: { responsive: true }
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
                .catch(() => showAlert('Error', 'Could not fetch availability data', 'error'));
        });
    }

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

    function loadBookings() {
        if (document.getElementById('bookingTable')) {
            fetch('/admin-dashboard/bookings/')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.querySelector('#bookingTable tbody');
                    tbody.innerHTML = data.map(item => `
                        <tr data-id="${item.id}">
                            <td>${item.user}</td>
                            <td>${item.classroom}</td>
                            <td>${item.date}</td>
                            <td>${item.start_time} - ${item.end_time}</td>
                            <td>${item.status}</td>
                            <td class="form-group flex gap-2">
                                ${item.status === 'pending' ? `
                                    <button class="approve" onclick="approveBooking(${item.id})">Approve</button>
                                    <button class="reject" onclick="rejectBooking(${item.id})">Reject</button>
                                ` : ''}
                            </td>
                        </tr>
                    `).join('');
                    document.getElementById('bookingTable').style.display = 'table';
                    document.getElementById('bookingLoading').style.display = 'none';
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
        })
        .then(() => {
            showAlert('Saved!', 'Timetable entry updated successfully');
            loadTimetable();
        })
        .catch(() => showAlert('Error', 'Failed to save timetable', 'error'));
    };

    window.deleteTimetable = function(id) {
        Swal.fire({
            title: 'Delete entry?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ADD8E6',
            cancelButtonColor: '#dc3545'
        }).then(result => {
            if (result.isConfirmed) {
                fetch(`/admin-dashboard/timetable/delete/${id}/`, {
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': getCSRFToken() }
                })
                .then(() => {
                    showAlert('Deleted!', 'Timetable entry deleted successfully');
                    loadTimetable();
                })
                .catch(() => showAlert('Error', 'Failed to delete timetable', 'error'));
            }
        });
    };

    window.approveBooking = function(id) {
        fetch(`/admin-dashboard/bookings/${id}/approve/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(() => {
            showAlert('Approved!', 'Booking approved successfully');
            loadBookings();
        })
        .catch(() => showAlert('Error', 'Failed to approve booking', 'error'));
    };

    window.rejectBooking = function(id) {
        fetch(`/admin-dashboard/bookings/${id}/reject/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(() => {
            showAlert('Rejected!', 'Booking rejected successfully');
            loadBookings();
        })
        .catch(() => showAlert('Error', 'Failed to reject booking', 'error'));
    };

    window.exportCSV = function() {
        window.location.href = '/admin-dashboard/timetable/export/';
    };

    initCharts();
    loadTimetable();
    loadBookings();
});
