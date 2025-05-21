document.addEventListener('DOMContentLoaded', function () {
    const dropzone = document.querySelector('.dropzone');
    const fileInput = document.querySelector('#fileInput');
    const filePreview = document.getElementById('filePreview');
    const uploadForm = document.getElementById('uploadForm');

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
                filePreview.textContent = `Selected: ${files[0].name}`;
                filePreview.classList.remove('hidden');
            }
        });
        dropzone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                filePreview.textContent = `Selected: ${fileInput.files[0].name}`;
                filePreview.classList.remove('hidden');
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            if (!fileInput.files.length) {
                e.preventDefault();
                Swal.fire('Warning', 'Please select a file to upload.', 'warning');
            }
        });
    }

    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function () {
            document.body.classList.toggle('dark');
            localStorage.setItem('darkMode', document.body.classList.contains('dark') ? 'enabled' : 'disabled');
        });
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark');
        }
    }
});
