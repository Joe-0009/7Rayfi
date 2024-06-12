from flask import Blueprint, flash, render_template, request


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("logout.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firsName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        if len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
            
        elif len(firsName) <  2:
            flash('first name must be greater than 4 characters.', category='error')
        elif len(password1) < 7:
            flash("passwords don't match'", category='error')
        else:
            flash('Account created successfull')
            
    return render_template("sign_up.html")