from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import JobForm, DummyForm, RatingForm
from ..models import Job, User, Application
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
            if picture.filename:
                filename = secure_filename(picture.filename)
                picture_path = os.path.join(current_app.config['UPLOAD_FOLDER2'], filename)
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
    form = DummyForm()
    return render_template('job/view_jobs.html', jobs=jobs, form=form)

@job.route('/delete-job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.poster_id != current_user.id:
        flash('You do not have permission to delete this job', 'danger')
        return redirect(url_for('job.view_jobs'))
    
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('job.view_jobs'))

@job.route('/apply-job/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user in job.applied_by:
        flash('You have already applied for this job', 'warning')
    else:
        job.applied_by.append(current_user)
        db.session.commit()
        flash('Successfully applied for the job!', 'success')
    return redirect(url_for('job.view_jobs'))

@job.route('/finish-job/<int:job_id>', methods=['POST'])
@login_required
def finish_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.poster_id != current_user.id:
        flash('You are not authorized to finish this job', 'danger')
        return redirect(url_for('job.view_jobs'))

    job.status = 'Finished'
    db.session.commit()
    flash('Job marked as finished!', 'success')
    return redirect(url_for('job.view_jobs'))


@job.route('/rate-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def rate_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.status != 'Finished':
        flash('You can only rate a finished job', 'danger')
        return redirect(url_for('job.view_jobs'))

    form = RatingForm()
    if form.validate_on_submit():
        job.rating = form.rating.data
        db.session.commit()
        flash('Rating submitted successfully!', 'success')
        return redirect(url_for('job.view_jobs'))

    return render_template('job/rate_job.html', form=form, job=job)



@job.route('/job/<int:job_id>')
@login_required
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job_id).all()
    return render_template('job/job_details.html', job=job, applications=applications)

@job.route('/accept-application/<int:application_id>', methods=['POST'])
@login_required
def accept_application(application_id):
    application = Application.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)
    if job.poster_id != current_user.id:
        flash('You are not authorized to accept applications for this job', 'danger')
        return redirect(url_for('job.job_details', job_id=job.id))
    
    job.accepted_worker_id = application.worker_id
    db.session.commit()
    flash('You have accepted an application', 'success')
    return redirect(url_for('job.job_details', job_id=job.id))