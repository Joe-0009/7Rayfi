document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.my-jobs-container .tab-button');
    const tabContents = document.querySelectorAll('.my-jobs-container .tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
});