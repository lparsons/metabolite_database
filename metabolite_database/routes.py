from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from metabolite_database import app
from metabolite_database import db
from metabolite_database.forms import LoginForm
from metabolite_database.models import Compound
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import RetentionTime


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Lance'}
    return render_template('index.html', title='Home', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/compounds')
def compounds():
    compounds = Compound.query.all()
    return render_template('compounds.html', compounds=compounds)


@app.route('/compound/<id>')
def compound(id):
    compound = Compound.query.get(id)
    return render_template('compound.html', compound=compound)


@app.route('/methods')
def methods():
    methods = ChromatographyMethod.query.all()
    return render_template('methods.html', methods=methods)


@app.route('/retention_times/<method>')
@app.route('/retention-times/<method>')
@app.route('/retentiontimes/<method>')
def retention_times(method):
    method = ChromatographyMethod.query.filter(
        ChromatographyMethod.name == method).first_or_404()
    results = db.session.query(Compound, RetentionTime).\
        join(RetentionTime).\
        filter(RetentionTime.chromatography_method.has(name=method.name))
    return render_template('retention_times.html', method=method,
                           results=results)
