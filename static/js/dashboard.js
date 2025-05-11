document.addEventListener('DOMContentLoaded', function () {
    // Sidebar Toggle
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.querySelector('.sidebar-toggle');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('hidden');
            sidebar.classList.toggle('active');
        });
    }

    // Messages with SweetAlert
    const messages = document.querySelectorAll('.messages .message');
    messages.forEach(message => {
        const type = message.classList.contains('success') ? 'success' :
            message.classList.contains('error') ? 'error' : 'info';
        Swal.fire({
            icon: type,
            title: type.charAt(0).toUpperCase() + type.slice(1),
            text: message.textContent,
            confirmButtonColor: '#0071E3'
        });
    });

    // Form Validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const inputs = form.querySelectorAll('input[required], select[required]');
            let valid = true;
            inputs.forEach(input => {
                if (!input.value) {
                    valid = false;
                    input.classList.add('border-red-500');
                } else {
                    input.classList.remove('border-red-500');
                }
            });
            if (!valid) {
                e.preventDefault();
                Swal.fire({
                    icon: 'warning',
                    title: 'Missing Fields',
                    text: 'Please fill in all required fields.',
                    confirmButtonColor: '#0071E3'
                });
            }
        });
    });

    // Block Filter Auto-Submit (for forms, not dashboard filters)
    const blockFilters = document.querySelectorAll('select[name="block"]');
    blockFilters.forEach(filter => {
        filter.addEventListener('change', function () {
            if (this.form) this.form.submit();
        });
    });

    // Date and Time Validation
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const timeInputs = document.querySelectorAll('input[type="time"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function () {
            const today = new Date().toISOString().split('T')[0];
            if (this.value < today) {
                this.value = today;
                Swal.fire({
                    icon: 'warning',
                    title: 'Invalid Date',
                    text: 'Cannot select a past date.',
                    confirmButtonColor: '#0071E3'
                });
            }
        });
    });
    timeInputs.forEach(input => {
        input.addEventListener('change', function () {
            const form = this.form;
            const startTime = form.querySelector('input[name="start_time"]');
            const endTime = form.querySelector('input[name="end_time"]');
            if (startTime && endTime && startTime.value && endTime.value) {
                if (startTime.value >= endTime.value) {
                    endTime.value = '';
                    Swal.fire({
                        icon: 'warning',
                        title: 'Invalid Time',
                        text: 'End time must be after start time.',
                        confirmButtonColor: '#0071E3'
                    });
                }
            }
        });
    });

    // Drag-and-Drop for Timetable Upload
    const dropzone = document.querySelector('.dropzone');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
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
                filePreview.classList.remove('hidden');
                filePreview.textContent = `Selected file: ${files[0].name}`;
            }
        });
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                filePreview.classList.remove('hidden');
                filePreview.textContent = `Selected file: ${fileInput.files[0].name}`;
            }
        });
    }

    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeIcon = document.getElementById('darkModeIcon');
    if (darkModeToggle) {
        // Check initial dark mode state from localStorage
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        document.body.classList.toggle('dark', isDarkMode);
        updateDarkModeIcon(isDarkMode);

        darkModeToggle.addEventListener('click', () => {
            const isDark = document.body.classList.toggle('dark');
            localStorage.setItem('darkMode', isDark);
            updateDarkModeIcon(isDark);
            // Send preference to server to persist in session
            fetch('/toggle-dark-mode/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ dark_mode: isDark }),
            }).catch(error => console.error('Error saving dark mode:', error));
        });
    }
    function updateDarkModeIcon(isDark) {
        darkModeIcon.innerHTML = isDark
            ? '<path d="M12 3v2.25m0 13.5V21m-8.25-9h2.25m13.5 0h-2.25m-9-9l2.25 2.25m4.5 4.5l-2.25 2.25m0-9l-2.25 2.25m4.5 4.5l2.25-2.25"></path>' // Sun icon
            : '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>'; // Moon icon
    }

    // Approve/Reject Booking Actions
    function handleBookingAction(bookingId, action) {
        Swal.fire({
            title: `Processing...`,
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });
        const url = action === 'approve'
            ? `/admin-dashboard/api/bookings/approve/${bookingId}/`
            : `/admin-dashboard/api/bookings/reject/${bookingId}/`;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
        })
            .then(response => response.json())
            .then(data => {
                Swal.close();
                if (data.error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.error,
                    });
                } else {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: data.message,
                    });
                    const row = document.querySelector(`#booking-${bookingId}`);
                    const statusElement = row.querySelector('.status');
                    if (statusElement) {
                        statusElement.textContent = action === 'approve' ? 'Approved' : 'Rejected';
                        statusElement.className = `status badge ${action === 'approve' ? 'bg-success' : 'bg-danger'}`;
                    }
                    // Hide action buttons after approval/rejection
                    const actionsCell = row.querySelector('td:last-child');
                    if (actionsCell) {
                        actionsCell.innerHTML = '';
                    }
                }
            })
            .catch(error => {
                Swal.close();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'An error occurred while processing the request.',
                });
                console.error('Error:', error);
            });
    }
    document.querySelectorAll('.approve-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const bookingId = e.target.dataset.bookingId;
            handleBookingAction(bookingId, 'approve');
        });
    });
    document.querySelectorAll('.reject-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const bookingId = e.target.dataset.bookingId;
            handleBookingAction(bookingId, 'reject');
        });
    });

    // --- DASHBOARD CHARTS SECTION ---

    // Chart.js chart instances
    let usageChart = null;
    let peakHoursChart = null;
    let activeFacultyChart = null;

    // Get filter elements
    const blockFilter = document.getElementById('blockFilter');
    const dayFilter = document.getElementById('dayFilter');

    // Utility to get current filter values
    function getFilters() {
        return {
            block: blockFilter ? blockFilter.value : '',
            day: dayFilter ? dayFilter.value : ''
        };
    }

    // Utility to build URL with query params
    function buildUrl(url, params) {
        const usp = new URLSearchParams();
        for (const key in params) {
            if (params[key]) usp.append(key, params[key]);
        }
        return url + (usp.toString() ? '?' + usp.toString() : '');
    }

    // Classroom Usage Chart
    function loadUsageChart() {
        const { block, day } = getFilters();
        fetch(buildUrl('/admin-dashboard/api/stats/usage/', { block, day }))
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('usageChart').getContext('2d');
                if (usageChart) usageChart.destroy();
                usageChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Usage Count',
                            data: data.data,
                            backgroundColor: 'rgba(54, 162, 235, 0.7)'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: { y: { beginAtZero: true } }
                    }
                });
            })
            .catch(() => {
                alert('Failed to load Classroom Usage chart.');
            });
    }

    // Peak Hours Chart
    function loadPeakHoursChart() {
        const { day } = getFilters();
        fetch(buildUrl('/admin-dashboard/api/stats/peakhours/', { day }))
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('peakHoursChart').getContext('2d');
                if (peakHoursChart) peakHoursChart.destroy();
                peakHoursChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Classes',
                            data: data.data,
                            backgroundColor: 'rgba(255, 159, 64, 0.7)'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: { y: { beginAtZero: true } }
                    }
                });
            })
            .catch(() => {
                alert('Failed to load Peak Hours chart.');
            });
    }

    // Active Faculty Chart
    function loadActiveFacultyChart() {
        const { block } = getFilters();
        fetch(buildUrl('/admin-dashboard/api/stats/faculty/', { block }))
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('activeFacultyChart').getContext('2d');
                if (activeFacultyChart) activeFacultyChart.destroy();
                activeFacultyChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Active Classes',
                            data: data.data,
                            backgroundColor: 'rgba(75, 192, 192, 0.7)'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: { y: { beginAtZero: true } }
                    }
                });
            })
            .catch(() => {
                alert('Failed to load Active Faculty chart.');
            });
    }

    // Load all charts
    function loadAllCharts() {
        loadUsageChart();
        loadPeakHoursChart();
        loadActiveFacultyChart();
    }

    // Attach filter change event handlers
    if (blockFilter) blockFilter.addEventListener('change', loadAllCharts);
    if (dayFilter) dayFilter.addEventListener('change', loadAllCharts);

    // Initial load
    loadAllCharts();

    // Helper function to get CSRF token
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
});

