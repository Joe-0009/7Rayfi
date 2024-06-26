import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import UpdateProfileForm, AddSkillForm, AddExperienceForm, DummyForm
from ..models import User, Skill, Experience, Certification, Job, Review, Application
from .. import db
from sqlalchemy.sql import func

profile = Blueprint('profile', __name__)


@profile.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    profile_user = User.query.get_or_404(user_id)
    skills = profile_user.skills
    experiences = profile_user.experiences
    certifications = profile_user.certifications
    reviews = profile_user.reviews_received
    average_rating = db.session.query(func.avg(Review.rating)).filter_by(reviewee_id=user_id).scalar()

    add_skill_form = AddSkillForm()
    add_experience_form = AddExperienceForm()
    dummy_form = DummyForm()
    applied_jobs = Job.query.join(Application).filter(Application.worker_id == user_id).all()
    reviews_received = profile_user.reviews_received
    posted_jobs = Job.query.filter_by(poster_id=user_id).all()

    return render_template('profile/profile.html', 
                           profile_user=profile_user, 
                           skills=skills, 
                           experiences=experiences, 
                           certifications=certifications, 
                           posted_jobs=posted_jobs, 
                           reviews=reviews, 
                           average_rating=average_rating,
                           add_skill_form=add_skill_form,
                           add_experience_form=add_experience_form,
                           form=dummy_form, 
                           reviews_received=reviews_received,
                           applied_jobs=applied_jobs)


@profile.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.location = form.location.data
        current_user.profession = form.profession.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.about_me = form.about_me.data
        
        file = request.files.get('profile_picture')
        if file:
            filename = secure_filename(file.filename)
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            current_user.profile_picture = filename
            
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.location.data = current_user.location
        form.profession.data = current_user.profession
        form.date_of_birth.data = current_user.date_of_birth
        form.about_me.data = current_user.about_me
    return render_template('profile/update_profile.html', form=form)


@profile.route('/add-skill', methods=['POST'])
@login_required
def add_skill():
    form = AddSkillForm()
    if form.validate_on_submit():
        skill = Skill(name=form.skill.data, user_id=current_user.id)
        db.session.add(skill)
        db.session.commit()
        flash('Skill added successfully!', 'success')
    else:
        flash('Failed to add skill. Please try again.', 'error')
    return redirect(url_for('profile.view_profile', user_id=current_user.id))


@profile.route('/add-experience', methods=['POST'])
@login_required
def add_experience():
    form = AddExperienceForm()
    if form.validate_on_submit():
        experience = Experience(title=form.experience.data, user_id=current_user.id)
        db.session.add(experience)
        db.session.commit()
        flash('Experience added successfully!', 'success')
    else:
        flash('Failed to add experience. Please try again.', 'error')
    return redirect(url_for('profile.view_profile', user_id=current_user.id))
