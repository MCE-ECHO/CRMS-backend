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

    // Messages
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

    // Auto-submit Block Filter
    const blockFilters = document.querySelectorAll('select[name="block"]');
    blockFilters.forEach(filter => {
        filter.addEventListener('change', function () {
            this.form.submit();
        });
    });

    // Date and Time Input Validation
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
});

