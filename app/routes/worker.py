from flask import Blueprint, render_template, flash
from flask_login import login_required
from ..forms import  SearchWorkersForm
from ..models import User, Skill

worker = Blueprint('worker', __name__)

@worker.route('/search-workers', methods=['GET', 'POST'])
@login_required
def search_workers():
    form = SearchWorkersForm()
    results = []
    if form.validate_on_submit():
        location = form.location.data
        profession = form.profession.data
        results = User.query.filter_by(location=location, profession=profession).all()
    return render_template('worker/search_workers.html', form=form, results=results)
