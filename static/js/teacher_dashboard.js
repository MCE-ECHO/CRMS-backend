document.addEventListener('DOMContentLoaded', function () {
    // Timetable Filtering (e.g., on admin timetable management page)
    const timetableTable = document.getElementById('timetableTable');
    if (timetableTable) {
        const filterDay = document.createElement('select');
        filterDay.innerHTML = `
            <option value="">All Days</option>
            <option value="Monday">Monday</option>
            <option value="Tuesday">Tuesday</option>
            <option value="Wednesday">Wednesday</option>
            <option value="Thursday">Thursday</option>
            <option value="Friday">Friday</option>
            <option value="Saturday">Saturday</option>
            <option value="Sunday">Sunday</option>
        `;
        filterDay.classList.add('mb-4', 'p-2', 'border', 'rounded-lg');
        timetableTable.parentElement.insertBefore(filterDay, timetableTable);

        let timetableData = [];
        fetch('/timetable/api/all/')
            .then(res => res.json())
            .then(data => {
                timetableData = data;
                renderTimetable(timetableData);
            })
            .catch(error => handleError(error, 'timetableTable', 'Failed to load timetable.'));

        filterDay.addEventListener('change', function () {
            const filteredData = this.value
                ? timetableData.filter(entry => entry.day === this.value)
                : timetableData;
            renderTimetable(filteredData);
        });

        function renderTimetable(data) {
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
        }
    }
});

// Reusing editTimetable and deleteTimetable from dashboard.js if loaded
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
                        window.location.reload(); // Refresh to update the table
                    } else {
                        throw new Error('Failed to delete.');
                    }
                })
                .catch(err => handleError(err, 'timetableTable', 'Failed to delete timetable entry.'));
        }
    });
}

