import os
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, current_app as app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import UpdateProfileForm
from .models import Note, User, Skill, Experience, Certification, Job, Review
from . import db
import json
from sqlalchemy.sql import func

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return jsonify({})

@views.route('/profile')
@login_required
def profile():
    user = User.query.get(current_user.id)
    skills = Skill.query.filter_by(user_id=user.id).all()
    experiences = Experience.query.filter_by(user_id=user.id).all()
    certifications = Certification.query.filter_by(user_id=user.id).all()
    posted_jobs = Job.query.filter_by(poster_id=user.id).all()
    applied_jobs = user.applied_jobs
    reviews = Review.query.filter_by(reviewee_id=user.id).all()
    average_rating = db.session.query(func.avg(Review.rating)).filter_by(reviewee_id=user.id).scalar()

    return render_template('profile.html', 
                           user=user, 
                           skills=skills, 
                           experiences=experiences, 
                           certifications=certifications, 
                           posted_jobs=posted_jobs, 
                           applied_jobs=applied_jobs, 
                           reviews=reviews, 
                           average_rating=average_rating)

@views.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        
        file = request.files.get('profile_picture')
        if file:
            filename = secure_filename(file.filename)
            # Ensure the directory exists
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            current_user.profile_picture = filename
            
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('views.profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.location.data = current_user.location
        form.about_me.data = current_user.about_me
    return render_template('update_profile.html', form=form)
