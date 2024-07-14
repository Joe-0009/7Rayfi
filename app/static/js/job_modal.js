function openJobModal(jobId) {
    fetch(`/job_details/${jobId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        document.getElementById('jobModalContent').innerHTML = html;
        $('#jobModal').modal('show');
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('jobModalContent').innerHTML = `
            <div class="alert alert-danger" role="alert">
                An error occurred while loading job details. Please try again later.
            </div>`;
        $('#jobModal').modal('show');
    });
}