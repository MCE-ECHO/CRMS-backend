document.addEventListener('DOMContentLoaded', function () {
    const ctxUsage = document.getElementById('usageChart');
    const ctxPeak = document.getElementById('peakHoursChart');
    const ctxFaculty = document.getElementById('activeFacultyChart');

    function updateChart(ctx, url, type, label) {
        fetch(url)
            .then(res => res.json())
            .then(data => {
                new Chart(ctx, {
                    type: type,
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: label,
                            data: data.data,
                            backgroundColor: type === 'line' ? undefined : '#0071E3',
                            borderColor: type === 'line' ? '#0071E3' : undefined,
                            fill: type === 'line' ? false : undefined
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            })
            .catch(error => handleError(error, ctx.id, `Failed to load ${label.toLowerCase()}.`));
    }

    // Usage Chart with Block Filter
    if (ctxUsage) {
        const blockFilter = document.getElementById('blockFilter');
        function fetchUsage() {
            let url = '/admin-dashboard/api/stats/usage/';
            if (blockFilter && blockFilter.value) {
                url += `?block=${blockFilter.value}`;
            }
            updateChart(ctxUsage, url, 'bar', 'Classroom Usage');
        }
        fetchUsage();
        if (blockFilter) {
            blockFilter.addEventListener('change', fetchUsage);
        }
    }

    // Peak Hours Chart
    if (ctxPeak) {
        updateChart(ctxPeak, '/admin-dashboard/api/stats/peakhours/', 'line', 'Peak Hours');
    }

    // Active Faculty Chart
    if (ctxFaculty) {
        updateChart(ctxFaculty, '/admin-dashboard/api/stats/faculty/', 'bar', 'Faculty Activity');
    }
});

