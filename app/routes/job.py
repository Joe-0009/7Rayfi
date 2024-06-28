import os
from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import JobForm, DummyForm, RatingForm, AcceptApplicationForm
from ..models import Job, User, Application, Review, JobPicture, ApplicationStatus, accepted_applicants
from .. import db
from datetime import datetime, timezone
from PIL import Image
from sqlalchemy.exc import IntegrityError

job = Blueprint('job', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@job.route('/post', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        new_job = Job(
            title=form.title.data,
            description=form.description.data,
            profession=form.profession.data,
            location=form.location.data,
            budget=form.budget.data,
            expected_duration=form.expected_duration.data,
            required_skills=form.required_skills.data,
            poster_id=current_user.id
        )
        db.session.add(new_job)
        db.session.flush()  # This assigns an ID to new_job

        # Handle picture uploads
        if form.pictures.data:
            for picture in form.pictures.data:
                if picture and allowed_file(picture.filename):
                    filename = secure_filename(picture.filename)
                    picture.save(os.path.join(current_app.config['UPLOAD_FOLDER2'], filename))
                    job_picture = JobPicture(filename=filename, job_id=new_job.id)
                    db.session.add(job_picture)

        db.session.commit()
        flash('Your job has been posted!', 'success')
        return redirect(url_for('home.index'))
    return render_template('job/post_job.html', title='Post a Job', form=form)

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
    if job.status != ApplicationStatus.OPEN:
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
        return redirect(url_for('job.job_details', job_id=job_id))

    if job.status != ApplicationStatus.IN_PROGRESS:
        flash('This job cannot be finished at this time', 'warning')
        return redirect(url_for('job.job_details', job_id=job_id))

    job.status = ApplicationStatus.COMPLETED
    db.session.commit()
    flash('Job marked as finished. Please rate the workers.', 'success')
    return redirect(url_for('job.rate_workers', job_id=job_id))

@job.route('/rate-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def rate_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.status != ApplicationStatus.COMPLETED:
        flash('You can only rate a finished job', 'danger')
        return redirect(url_for('job.view_jobs'))

    form = RatingForm()
    if form.validate_on_submit():
        job.rating = form.rating.data
        db.session.commit()
        flash('Rating submitted successfully!', 'success')
        return redirect(url_for('job.view_jobs'))

    return render_template('job/rate_job.html', form=form, job=job)

@job.route('/job_details/<int:job_id>', methods=['GET'])
@login_required
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job_id).all()
    user_applied = Application.query.filter_by(job_id=job_id, worker_id=current_user.id).first() is not None
    accept_form = AcceptApplicationForm()
    return render_template('job/job_details.html', job=job, applications=applications, accept_form=accept_form, user_applied=user_applied, ApplicationStatus=ApplicationStatus)

@job.route('/accept-application/<int:job_id>/<int:application_id>', methods=['POST'])
@login_required
def accept_application(job_id, application_id):
    job = Job.query.get_or_404(job_id)
    application = Application.query.get_or_404(application_id)
    
    if job.poster_id != current_user.id:
        flash('You are not authorized to accept applications for this job.', 'error')
        return redirect(url_for('job.job_details', job_id=job_id))

    if application.job_id != job_id:
        flash('This application does not belong to this job.', 'error')
        return redirect(url_for('job.job_details', job_id=job_id))

    # Check if the applicant is already accepted
    existing_acceptance = db.session.query(accepted_applicants).filter_by(job_id=job_id, user_id=application.worker_id).first()
    if existing_acceptance:
        flash('This applicant has already been accepted for this job.', 'error')
        return redirect(url_for('job.job_details', job_id=job_id))

    # Accept the application
    job.accepted_workers.append(application.applicant)
    application.status = ApplicationStatus.ACCEPTED
    try:
        db.session.commit()
        flash('Application accepted successfully!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Error: This applicant has already been accepted for this job.', 'error')

    return redirect(url_for('job.job_details', job_id=job_id))


@job.route('/rate-workers/<int:job_id>', methods=['GET', 'POST'])
@login_required
def rate_workers(job_id):
    job = Job.query.get_or_404(job_id)
    if job.poster_id != current_user.id:
        flash('You do not have permission to rate workers for this job', 'danger')
        return redirect(url_for('job.job_details', job_id=job_id))

    if job.status != ApplicationStatus.COMPLETED:
        flash('You can only rate workers for completed jobs', 'warning')
        return redirect(url_for('job.job_details', job_id=job_id))

    form = RatingForm()
    if form.validate_on_submit():
        for worker in job.accepted_workers:
            new_review = Review(
                reviewer_id=current_user.id,
                reviewee_id=worker.id,
                job_id=job.id,
                rating=form.rating.data,
                comment=form.review.data
            )
            db.session.add(new_review)
        db.session.commit()
        flash('Ratings submitted successfully!', 'success')
        return redirect(url_for('job.job_details', job_id=job_id))

    return render_template('job/rate_workers.html', form=form, job=job)