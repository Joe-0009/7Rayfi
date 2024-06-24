from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import JobForm, DummyForm
from ..models import Job
from .. import db
from datetime import datetime
import os

job = Blueprint('job', __name__)

@job.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        picture_files = form.pictures.data
        picture_filenames = []
        
        for picture in picture_files:
            if picture.filename != '':
                filename = secure_filename(picture.filename)
                picture_path = os.path.join(current_app.config['UPLOAD_FOLDER2'], filename)
                picture.save(picture_path)
                picture_filenames.append(filename)
        
        new_job = Job(
            title=form.title.data,
            description=form.description.data,
            profession=form.profession.data,
            location=form.location.data,
            pictures=','.join(picture_filenames) if picture_filenames else None,
            status='Open',
            date_posted=datetime.now(),
            poster_id=current_user.id
        )
        
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('job.view_jobs'))
    
    return render_template('job/post_job.html', form=form)

@job.route('/jobs')
@login_required
def view_jobs():
    jobs = Job.query.all()
    form = DummyForm()  # Dummy form for CSRF token
    return render_template('job/view_jobs.html', jobs=jobs, form=form)

@job.route('/delete-job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.poster_id != current_user.id:
        flash('You do not have permission to delete this job.', 'danger')
        return redirect(url_for('job.view_jobs'))

    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('job.view_jobs'))
