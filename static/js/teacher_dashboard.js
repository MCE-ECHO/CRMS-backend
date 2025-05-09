document.addEventListener('DOMContentLoaded', function () {
    // Filter Timetable
    const dayFilter = document.getElementById('dayFilter');
    if (dayFilter) {
        dayFilter.addEventListener('change', function () {
            const selectedDay = this.value;
            const rows = document.querySelectorAll('.timetable-row');
            rows.forEach(row => {
                if (!selectedDay || row.dataset.day === selectedDay) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Fetch Teacher's Timetable
    const timetableTable = document.getElementById('teacherTimetable');
    if (timetableTable) {
        fetch('/timetable/api/all/')
            .then(res => res.json())
            .then(data => {
                const tbody = timetableTable.querySelector('tbody');
                tbody.innerHTML = data
                    .filter(entry => entry.teacher === currentUser)
                    .map(entry => `
                        <tr class="timetable-row" data-day="${entry.day}">
                            <td>${entry.classroom}</td>
                            <td>${entry.day}</td>
                            <td>${entry.start_time}</td>
                            <td>${entry.end_time}</td>
                            <td>${entry.subject_name || 'N/A'}</td>
                        </tr>
                    `).join('');
                timetableTable.style.display = 'table';
            })
            .catch(error => handleError(error, 'teacherTimetable', 'Failed to load timetable.'));
    }

    // Fetch Teacher's Bookings
    const bookingsTable = document.getElementById('teacherBookings');
    if (bookingsTable) {
        fetch('/booking/admin/list/')
            .then(res => res.json())
            .then(data => {
                const tbody = bookingsTable.querySelector('tbody');
                tbody.innerHTML = data
                    .filter(booking => booking.user === currentUser)
                    .map(booking => `
                        <tr>
                            <td>${booking.classroom}</td>
                            <td>${booking.date}</td>
                            <td>${booking.start_time}</td>
                            <td>${booking.end_time}</td>
                            <td>${booking.status}</td>
                        </tr>
                    `).join('');
                bookingsTable.style.display = 'table';
            })
            .catch(error => handleError(error, 'teacherBookings', 'Failed to load bookings.'));
    }

    // Booking Form
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function (e) {
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
                        bookingForm.reset();
                        bookingsTable.dispatchEvent(new Event('load'));
                    } else {
                        Swal.fire('Error', data.error || 'Failed to create booking.', 'error');
                    }
                })
                .catch(err => handleError(err, 'bookingForm', 'Failed to create booking.'));
        });
    }
});

