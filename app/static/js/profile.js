

document.getElementById('add-skill-link').addEventListener('click', function(e) {
    e.preventDefault();
    var form = document.getElementById('add-skill-form');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        this.textContent = '- Cancel';
    } else {
        form.style.display = 'none';
        this.textContent = '+ Add Skill';
    }
});


document.getElementById('add-experience-link').addEventListener('click', function(e) {
    e.preventDefault();
    var form = document.getElementById('add-experience-form');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        this.textContent = '- Cancel';
    } else {
        form.style.display = 'none';
        this.textContent = '+ Add Experience';
    }
});