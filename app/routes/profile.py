#profile.py
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import UpdateProfileForm, AddSkillForm, AddExperienceForm, DummyForm
from ..models import User, Skill, Experience, Certification, Job, Review, Application
from .. import db
from sqlalchemy.sql import func
from PIL import Image

profile = Blueprint('profile', __name__)

def save_picture(file):
    """Save and resize uploaded profile picture, return filename."""
    filename = secure_filename(file.filename)
    _, ext = os.path.splitext(filename)
    new_filename = f"{current_user.id}{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, new_filename)
    
    # Resize image
    output_size = (250, 250)
    img = Image.open(file)
    img.thumbnail(output_size)
    img.save(filepath)
    
    return new_filename

@profile.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    """View user profile."""
    profile_user = User.query.get_or_404(user_id)
    average_rating = db.session.query(func.avg(Review.rating)).filter_by(reviewee_id=user_id).scalar() or 0
    applied_jobs = Application.query.filter_by(worker_id=user_id).all()
    posted_jobs = Job.query.filter_by(poster_id=user_id).all()
    reviews = Review.query.filter_by(reviewee_id=user_id).all()
    
    return render_template('profile/profile.html', 
                           profile_user=profile_user, 
                           average_rating=average_rating,
                           add_skill_form=AddSkillForm(),
                           add_experience_form=AddExperienceForm(),
                           form=DummyForm(), 
                           applied_jobs=applied_jobs,
                           posted_jobs=posted_jobs,
                           )

@profile.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """Update user profile."""
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.location = form.location.data
        current_user.profession = form.profession.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.about_me = form.about_me.data
        
        if form.profile_picture.data:
            current_user.profile_picture = save_picture(form.profile_picture.data)
            
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))
    
    form.process(obj=current_user)
    return render_template('profile/update_profile.html', form=form)

@profile.route('/add-skill', methods=['POST'])
@login_required
def add_skill():
    """Add a new skill to user profile."""
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
    """Add a new experience to user profile."""
    form = AddExperienceForm()
    if form.validate_on_submit():
        experience = Experience(title=form.experience.data, user_id=current_user.id)
        db.session.add(experience)
        db.session.commit()
        flash('Experience added successfully!', 'success')
    else:
        flash('Failed to add experience. Please try again.', 'error')
    return redirect(url_for('profile.view_profile', user_id=current_user.id))