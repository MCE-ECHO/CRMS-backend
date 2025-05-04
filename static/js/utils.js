// Utility Functions
function getCSRFToken() {
    return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
}

function showAlert(title, message, icon = 'success') {
    Swal.fire({
        title: title,
        text: message,
        icon: icon,
        confirmButtonColor: '#ADD8E6',
    });
}

function handleError(error, elementId, message) {
    document.getElementById(elementId).innerHTML = `<p class="text-red-500">${message}</p>`;
    console.error(error);
}
