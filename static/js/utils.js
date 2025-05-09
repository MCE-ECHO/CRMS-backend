function handleError(error, elementId, message) {
    console.error(error);
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<p class="text-red-500">${message}</p>`;
    }
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message,
        confirmButtonColor: '#0071E3'
    });
}

function ajaxGet(url, callback) {
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => callback(null, data))
        .catch(error => callback(error, null));
}

function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    return data;
}

