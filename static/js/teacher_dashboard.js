document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('teacherCalendar');
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'timeGridWeek',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'timeGridWeek,timeGridDay'
            },
            events: '/timetable/api/teacher/',
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
});
