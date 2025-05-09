document.addEventListener('DOMContentLoaded', function () {
    // Chart.js Usage, Peak Hours, Faculty
    const ctxUsage = document.getElementById('usageChart');
    const ctxPeak = document.getElementById('peakHoursChart');
    const ctxFaculty = document.getElementById('activeFacultyChart');

    function updateChart(ctx, url, type, label) {
        fetch(url)
            .then(res => res.json())
            .then(data => {
                new Chart(ctx, {
                    type: type,
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: label,
                            data: data.data,
                            backgroundColor: type === 'line' ? undefined : '#0071E3',
                            borderColor: type === 'line' ? '#0071E3' : undefined,
                            fill: type === 'line' ? false : undefined
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            })
            .catch(error => handleError(error, ctx.id, `Failed to load ${label.toLowerCase()}.`));
    }

    // Usage Chart with Block Filter
    if (ctxUsage) {
        const blockFilter = document.getElementById('blockFilter');
        function fetchUsage() {
            let url = '/admin-dashboard/usage/';
            if (blockFilter && blockFilter.value) {
                url += `?block=${blockFilter.value}`;
            }
            updateChart(ctxUsage, url, 'bar', 'Classroom Usage');
        }
        fetchUsage();
        if (blockFilter) {
            blockFilter.addEventListener('change', fetchUsage);
        }
    }

    // Peak Hours Chart
    if (ctxPeak) {
        updateChart(ctxPeak, '/admin-dashboard/peak-hours/', 'line', 'Peak Hours');
    }

    // Active Faculty Chart
    if (ctxFaculty) {
        updateChart(ctxFaculty, '/admin-dashboard/active-faculty/', 'bar', 'Faculty Activity');
    }

    // Drag and Drop Timetable Upload
    const dropzone = document.querySelector('.dropzone');
    const fileInput = document.querySelector('#fileInput');
    const filePreview = document.getElementById('filePreview');
    const uploadForm = document.getElementById('uploadForm');

    if (dropzone && fileInput && filePreview) {
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
                filePreview.textContent = `Selected: ${files[0].name}`;
                filePreview.classList.remove('hidden');
            }
        });

        dropzone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                filePreview.textContent = `Selected: ${fileInput.files[0].name}`;
                filePreview.classList.remove('hidden');
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            if (!fileInput.files.length) {
                e.preventDefault();
                Swal.fire('Warning', 'Please select a file to upload.', 'warning');
                return;
            }
            // Optionally, you can use AJAX to upload and show a message
        });
    }

    // Timetable Table (Admin)
    const timetableTable = document.getElementById('timetableTable');
    if (timetableTable) {
        fetch('/timetable/api/all/')
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
                document.getElementById('timetableLoading')?.style.display = 'none';
            })
            .catch(error => handleError(error, 'timetableTable', 'Failed to load timetable.'));
    }

    // Booking Table (Admin)
    const bookingTable = document.getElementById('bookingTable');
    if (bookingTable) {
        fetch('/booking/admin/list/')
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
                document.getElementById('bookingLoading')?.style.display = 'none';
            })
            .catch(error => handleError(error, 'bookingTable', 'Failed to load bookings.'));
    }
});

// Admin Timetable Actions (optional: implement modal/edit logic as needed)
function editTimetable(id) {
    Swal.fire('Info', 'Edit timetable functionality to be implemented.', 'info');
}

function deleteTimetable(id) {
    Swal.fire({
        title: 'Are you sure?',
        text: 'This will delete the timetable entry.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#0071E3',
        cancelButtonColor: '#E82127'
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/timetable/api/delete/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(res => {
                    if (res.ok) {
                        Swal.fire('Success', 'Timetable entry deleted.', 'success');
                        document.getElementById('timetableTable').querySelector('tbody').innerHTML = '';
                        document.getElementById('timetableTable').dispatchEvent(new Event('load'));
                    } else {
                        throw new Error('Failed to delete.');
                    }
                })
                .catch(err => handleError(err, 'timetableTable', 'Failed to delete timetable entry.'));
        }
    });
}

function approveBooking(id) {
    fetch(`/booking/admin/approve/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
        .then(res => res.json())
        .then(data => Swal.fire('Success', data.message, 'success'))
        .catch(err => handleError(err, 'bookingTable', 'Failed to approve booking.'));
}

function rejectBooking(id) {
    fetch(`/booking/admin/reject/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
        .then(res => res.json())
        .then(data => Swal.fire('Success', data.message, 'success'))
        .catch(err => handleError(err, 'bookingTable', 'Failed to reject booking.'));
}

function exportCSV() {
    window.location.href = '/timetable/api/export/';
}

