function handleError(error, elementId, message) {
    console.error(error);
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<p class="text-red-500">${message}</p>`;
    }
    Swal.fire('Error', message, 'error');
}
