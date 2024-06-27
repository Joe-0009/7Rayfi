import os
from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import JobForm, DummyForm, RatingForm
from ..models import Job, User, Application, Review
from .. import db
from datetime import datetime, timezone
from PIL import Image

job = Blueprint('job', __name__)

def save_pictures(pictures):
    """Save and resize uploaded job pictures, return filenames."""
    picture_filenames = []
    for picture in pictures:
        if picture.filename:
            filename = secure_filename(picture.filename)
            _, ext = os.path.splitext(filename)
            new_filename = f"{current_user.id}_{datetime.now().timestamp()}{ext}"
            picture_path = os.path.join(current_app.config['UPLOAD_FOLDER2'], new_filename)
            
            # Resize image
            output_size = (800, 600)
            img = Image.open(picture)
            img.thumbnail(output_size)
            img.save(picture_path)
            
            picture_filenames.append(new_filename)
    return picture_filenames

@job.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        picture_filenames = save_pictures(form.pictures.data)
        
        new_job = Job(
            title=form.title.data,
            description=form.description.data,
            profession=form.profession.data,
            location=form.location.data,
            pictures=','.join(picture_filenames),
            status='Open',
            date_posted=datetime.now(timezone.utc),
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
    jobs = Job.query.order_by(Job.date_posted.desc()).all()
    return render_template('job/view_jobs.html', jobs=jobs, form=DummyForm())

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
    if job.status != 'Open':
        flash('This job is no longer open for applications', 'warning')
        return redirect(url_for('job.view_jobs'))
    
    application = Application.query.filter_by(job_id=job_id, worker_id=current_user.id).first()
    if application:
        flash('You have already applied for this job', 'warning')
    else:
        new_application = Application(job_id=job_id, worker_id=current_user.id, date_applied=datetime.now(timezone.utc))
        db.session.add(new_application)
        db.session.commit()
        flash('Successfully applied for the job!', 'success')
    return redirect(url_for('job.view_jobs'))

@job.route('/finish-job/<int:job_id>', methods=['POST'])
@login_required
def finish_job(job_id):
    job = Job.query.get_or_404(job_id)

    if job.poster_id != current_user.id:
        flash('You do not have permission to finish this job', 'danger')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    form = RatingForm()
    if form.validate_on_submit():
        new_review = Review(
            reviewer_id=current_user.id,
            reviewee_id=job.accepted_worker_id,
            rating=form.rating.data,
            comment=form.review.data
        )
        db.session.add(new_review)
        job.status = 'Finished'
        db.session.commit()
        flash('Job finished and review submitted!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    return redirect(url_for('profile.view_profile', user_id=current_user.id))

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

@job.route('/accept-application/<int:job_id>/<int:application_id>', methods=['POST'])
@login_required
def accept_application(job_id, application_id):
    job = Job.query.get_or_404(job_id)
    application = Application.query.get_or_404(application_id)

    if job.poster_id != current_user.id:
        flash('You do not have permission to accept applications for this job', 'danger')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    if job.status != 'Open':
        flash('This job is no longer open for applications', 'warning')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    job.accepted_worker_id = application.worker_id
    job.status = 'In Progress'
    db.session.commit()
    flash('Application accepted!', 'success')

    return redirect(url_for('profile.view_profile', user_id=current_user.id))