from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename  # Import secure_filename
from ..forms import JobForm
from ..models import Job
from .. import db
from datetime import datetime
import os  # Import the os module

job = Blueprint('job', __name__)

@job.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        picture_files = form.pictures.data
        picture_filenames = []
        
        for picture in picture_files:
            filename = secure_filename(picture.filename)
            picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            picture.save(picture_path)
            picture_filenames.append(filename)
        
        new_job = Job(
            title=form.title.data,
            description=form.description.data,
            profession=form.profession.data,
            location=form.location.data,
            pictures=','.join(picture_filenames),
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
    return render_template('job/view_jobs.html', jobs=jobs)