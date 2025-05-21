// Utility Functions for API and UI

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toISOString().split('T')[0];
}

function formatTime(timeStr) {
    const [hours, minutes] = timeStr.split(':');
    const date = new Date();
    date.setHours(hours, minutes);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function makeApiRequest(url, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    };
    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }
    return fetch(url, options)
        .then(res => {
            if (!res.ok) throw new Error(`API request failed: ${res.statusText}`);
            return res.json();
        });
}

// Debounce Utility for Input Events
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

