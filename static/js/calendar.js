document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'timeGridWeek',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'timeGridWeek,timeGridDay,dayGridMonth'
            },
            events: function (fetchInfo, successCallback, failureCallback) {
                fetch('/timetable/api/all/')
                    .then(res => res.json())
                    .then(data => {
                        const events = data.map(entry => ({
                            title: `${entry.classroom} - ${entry.subject_name || 'N/A'}`,
                            start: `${fetchInfo.startStr.split('T')[0]}T${entry.start_time}`,
                            end: `${fetchInfo.startStr.split('T')[0]}T${entry.end_time}`,
                            daysOfWeek: [getDayIndex(entry.day)],
                            extendedProps: {
                                teacher: entry.teacher,
                                description: `Teacher: ${entry.teacher}\nSubject: ${entry.subject_name || 'N/A'}`
                            }
                        }));
                        successCallback(events);
                    })
                    .catch(error => {
                        handleError(error, 'calendar', 'Failed to load timetable.');
                        failureCallback(error);
                    });
            },
            eventClick: function (info) {
                Swal.fire({
                    title: info.event.title,
                    text: info.event.extendedProps.description || 'No description available',
                    icon: 'info',
                    confirmButtonColor: '#0071E3'
                });
            },
            slotMinTime: '08:00:00',
            slotMaxTime: '22:00:00',
            allDaySlot: false,
            responsive: true
        });
        calendar.render();
    }

    function getDayIndex(day) {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return days.indexOf(day);
    }
});
  
