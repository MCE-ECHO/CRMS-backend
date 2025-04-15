// CSRF Token Helper
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

// Form Validation Helper
function validateForm(form) {
    let isValid = true;
    form.querySelectorAll('input[required]').forEach(input => {
        if (!input.value) {
            isValid = false;
            input.classList.add('border-red-500');
        } else {
            input.classList.remove('border-red-500');
        }
    });
    return isValid;
}
