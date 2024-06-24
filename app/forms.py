# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField, DateField, MultipleFileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import User
from flask_wtf.file import FileAllowed
from datetime import datetime

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists.')
        
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = SelectField('Location', choices=[('Casablanca', 'Casablanca'), ('Rabat', 'Rabat'), ('Marrakech', 'Marrakech'), ('Kenitra', 'Kenitra'), ('Fes', 'Fes')], validators=[DataRequired()])
    profession = SelectField('Profession', choices=[('Electrician', 'Electrician'), ('Barber', 'Barber'), ('Tailor', 'Tailor'), ('Plumber', 'Plumber')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d')
    about_me = TextAreaField('About Me')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Profile')


class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired(), Length(min=10)])
    profession = SelectField('Profession', choices=[('Electrician', 'Electrician'), ('Barber', 'Barber'), ('Tailor', 'Tailor'), ('Plumber', 'Plumber')], validators=[DataRequired()])
    location = SelectField('Location', choices=[('Casablanca', 'Casablanca'), ('Rabat', 'Rabat'), ('Marrakech', 'Marrakech'), ('Kenitra', 'Kenitra'), ('Fes', 'Fes')], validators=[DataRequired()])
    pictures = MultipleFileField('Job Pictures', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Post Job')
    
    
class SearchWorkersForm(FlaskForm):
    location = SelectField('Location', choices=[('Casablanca', 'Casablanca'), ('Rabat', 'Rabat'), ('Marrakech', 'Marrakech'), ('Kenitra', 'Kenitra'), ('Fes', 'Fes')], validators=[DataRequired()])
    profession = SelectField('Profession', choices=[('Electrician', 'Electrician'), ('Barber', 'Barber'), ('Tailor', 'Tailor'), ('Plumber', 'Plumber')], validators=[DataRequired()])
    submit = SubmitField('Search')
    
class AddSkillForm(FlaskForm):
    skill = StringField('Skill', validators=[DataRequired()])
    submit = SubmitField('Add Skill')
    
class AddExperienceForm(FlaskForm):
    experience = StringField('Experience', validators=[DataRequired()])
    submit = SubmitField('Add Experience')
    
class DummyForm(FlaskForm):
    submit = SubmitField('Delete')
    
class DummyForm(FlaskForm):
    pass