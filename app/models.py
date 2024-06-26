from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date, datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    location = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    about_me = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    skills = db.relationship('Skill', backref='user', lazy=True)
    experiences = db.relationship('Experience', backref='user', lazy=True)
    certifications = db.relationship('Certification', backref='user', lazy=True)
    posted_jobs = db.relationship('Job', backref='poster', lazy=True, foreign_keys='Job.poster_id')
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy=True)
    applied_jobs = db.relationship('Job', secondary='application', backref='applicants', lazy='dynamic')

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    duration = db.Column(db.String(50))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    profession = db.Column(db.String(50))
    location = db.Column(db.String(100))
    pictures = db.Column(db.String(500))  # Store picture filenames as comma-separated string
    status = db.Column(db.String(50), default='Open')
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer, nullable=True)
    accepted_worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    applications = db.relationship('Application', backref='job', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_applied = db.Column(db.DateTime(timezone=True), default=func.now())

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
