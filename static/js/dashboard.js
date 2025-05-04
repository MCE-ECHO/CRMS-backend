document.addEventListener('DOMContentLoaded', function() {
    // Charts
    const ctxUsage = document.getElementById('usageChart');
    const ctxPeak = document.getElementById('peakHoursChart');
    const ctxFaculty = document.getElementById('activeFacultyChart');

    if (ctxUsage) {
        fetch('/admin-dashboard/usage/')
            .then(res => res.json())
            .then(data => {
                new Chart(ctxUsage, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Classroom Usage',
                            data: data.data,
                            backgroundColor: '#0071E3'
                        }]
                    }
                });
            });
    }

    if (ctxPeak) {
        fetch('/admin-dashboard/peak-hours/')
            .then(res => res.json())
            .then(data => {
                new Chart(ctxPeak, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Peak Hours',
                            data: data.data,
                            borderColor: '#0071E3',
                            fill: false
                        }]
                    }
                });
            });
    }

    if (ctxFaculty) {
        fetch('/admin-dashboard/active-faculty/')
            .then(res => res.json())
            .then(data => {
                new Chart(ctxFaculty, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Faculty Activity',
                            data: data.data,
                            backgroundColor: '#0071E3'
                        }]
                    }
                });
            });
    }

    // Drag and Drop
    const dropzone = document.querySelector('.dropzone');
    const fileInput = document.querySelector('#fileInput');
    const uploadForm = document.getElementById('uploadForm');

    if (dropzone && fileInput) {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                dropzone.textContent = `Selected: ${files[0].name}`;
            }
        });

        dropzone.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                dropzone.textContent = `Selected: ${fileInput.files[0].name}`;
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.message) {
                    Swal.fire('Success', data.message, 'success');
                }
                if (data.errors) {
                    Swal.fire('Warning', data.errors.join('<br>'), 'warning');
                }
            })
            .catch(err => Swal.fire('Error', 'Failed to upload file.', 'error'));
        });
    }

    // Timetable Table
    const timetableTable = document.getElementById('timetableTable');
    if (timetableTable) {
        fetch('/admin-dashboard/timetable/')
            .then(res => res.json())
            .then(data => {
                const tbody = timetableTable.querySelector('tbody');
                tbody.innerHTML = data.map(row => `
                    <tr>
                        <td>${row.day}</td>
                        <td>${row.start_time}</td>
                        <td>${row.end_time}</td>
                        <td>${row.classroom}</td>
                        <td>${row.teacher}</td>
                        <td>
                            <button onclick="editTimetable(${row.id})" class="btn btn-primary btn-sm">Edit</button>
                            <button onclick="deleteTimetable(${row.id})" class="btn btn-danger btn-sm">Delete</button>
                        </td>
                    </tr>
                `).join('');
                timetableTable.style.display = 'table';
                document.getElementById('timetableLoading').style.display = 'none';
            });
    }

    // Booking Table
    const bookingTable = document.getElementById('bookingTable');
    if (bookingTable) {
        fetch('/admin-dashboard/bookings/')
            .then(res => res.json())
            .then(data => {
                const tbody = bookingTable.querySelector('tbody');
                tbody.innerHTML = data.map(row => `
                    <tr>
                        <td>${row.user}</td>
                        <td>${row.classroom}</td>
                        <td>${row.date}</td>
                        <td>${row.start_time} - ${row.end_time}</td>
                        <td>${row.status}</td>
                        <td>
                            <button onclick="approveBooking(${row.id})" class="btn btn-primary btn-sm">Approve</button>
                            <button onclick="rejectBooking(${row.id})" class="btn btn-danger btn-sm">Reject</button>
                        </td>
                    </tr>
                `).join('');
                bookingTable.style.display = 'table';
                document.getElementById('bookingLoading').style.display = 'none';
            });
    }
});

function approveBooking(id) {
    fetch(`/admin-dashboard/bookings/${id}/approve/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(res => res.json())
    .then(data => Swal.fire('Success', data.message, 'success'))
    .catch(err => Swal.fire('Error', 'Failed to approve booking.', 'error'));
}

function rejectBooking(id) {
    fetch(`/admin-dashboard/bookings/${id}/reject/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(res => res.json())
    .then(data => Swal.fire('Success', data.message, 'success'))
    .catch(err => Swal.fire('Error', 'Failed to reject booking.', 'error'));
}

function exportCSV() {
    window.location.href = '/admin-dashboard/timetable/export/';
}
