from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from ..forms import JobForm
from ..models import Job
from .. import db
from datetime import datetime

job = Blueprint('job', __name__)

@job.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=form.description.data,
            status='Open',
            date_posted=datetime.now(),
            poster_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('job.view_jobs'))
    return render_template('job/post_job.html', form=form)

@job.route('/jobs')
@login_required
def view_jobs():
    jobs = Job.query.all()
    return render_template('job/view_jobs.html', jobs=jobs)
