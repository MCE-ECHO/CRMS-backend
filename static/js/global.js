document.addEventListener('DOMContentLoaded', function() {
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
});
