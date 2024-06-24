import os
from app import create_app, db
from app.models import User, Skill, Experience, Certification, Job, Review
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

with app.app_context():
    # Create the database and the database table
    db.create_all()

    # Add users
    users = [
        User(
            email='user1@example.com',
            username='user1',
            password=generate_password_hash('password', method='pbkdf2:sha256'),
            first_name='User',
            last_name='One',
            location='Casablanca',
            profession='Electrician',
            about_me='Experienced electrician',
            date_of_birth=date(1990, 1, 1)
        ),
        User(
            email='user2@example.com',
            username='user2',
            password=generate_password_hash('password', method='pbkdf2:sha256'),
            first_name='User',
            last_name='Two',
            location='Rabat',
            profession='Plumber',
            about_me='Experienced plumber',
            date_of_birth=date(1985, 5, 15)
        ),
        User(
            email='user3@example.com',
            username='user3',
            password=generate_password_hash('password', method='pbkdf2:sha256'),
            first_name='User',
            last_name='Three',
            location='Marrakech',
            profession='Barber',
            about_me='Experienced barber',
            date_of_birth=date(1992, 7, 20)
        )
    ]

    for user in users:
        db.session.add(user)

    # Commit the changes
    db.session.commit()

    print('Database seeded!')
